# -*- coding: utf-8 -*- ----------------------------------------------------===#
#
#  Copyright 2016-2025 Trovares Inc. dba Rocketgraph.  All rights reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#===------------------------------------------------------------------------===#

from __future__ import annotations

import collections
import glob
import numbers
import os
import re
import statistics
import sys
import time
import threading
import traceback
import weakref
import grpc
import pyarrow
import pyarrow.flight
import pyarrow.parquet
import pyarrow.csv

from collections.abc import Iterable, Mapping, Sequence
from datetime import timedelta, date, time as datetime_time, datetime
from decimal import Decimal
from ipaddress import IPv4Address, IPv6Address
from os.path import expanduser
from typing import Optional, Union, TYPE_CHECKING

from . import AdminService_pb2 as admin_proto
from . import AdminService_pb2_grpc as admin_grpc
from . import DataService_pb2 as data_proto
from . import DataService_pb2_grpc as data_grpc
from . import GraphTypesService_pb2 as graph_proto
from . import GraphTypesService_pb2_grpc as graph_grpc
from . import JobService_pb2 as job_proto
from . import JobService_pb2_grpc as job_grpc
from . import MetricsService_pb2 as metrics_proto
from . import MetricsService_pb2_grpc as metrics_grpc
from . import SchemaMessages_pb2 as sch_proto
from .common import (_assert_noerrors, _validated_property_name,
                     _validated_schema, _validated_frame_name,
                     _validated_namespace_name,
                     _validate_opt_level,
                     XgtError, XgtNameError, XgtConnectionError, XgtValueError,
                     XgtTypeError, XgtNotImplemented, XgtIOError, RowID,
                     _infer_xgt_schema_from_pyarrow_schema,
                     _find_key_in_schema, _apply_mapping_to_schema,
                     _remove_label_columns_from_schema,
                     _generate_proto_schema_from_xgt_schema,
                     _deprecated, DEFAULT_CHUNK_SIZE, MAX_PACKET_SIZE,
                     _validate_column_mapping_in_ingest,
                     _set_column_mapping_in_ingest_request, _group_paths,
                     _split_local_paths, _convert_header_mode, HeaderMode,
                     _process_protocol_version, TRUSTED_PROXY, FRAME_SEPARATOR,
                     _process_graph_members, _is_qualified_name,
                     _parse_qualified_name)
from .graph import (TableFrame, VertexFrame, EdgeFrame, GraphFrame, _group_paths)
from .job import Job
from .version import (
  __version__, __version_major__, __version_minor__, __version_patch__,
  __protobuf_major__, __protobuf_minor__, __protobuf_patch__,
  __protobuf_version__
)

def _add_version_number(request):
  request.protocol_version.major = int(__protobuf_major__)
  request.protocol_version.minor = int(__protobuf_minor__)
  request.protocol_version.patch = int(__protobuf_patch__)

def _check_version_number(response):
  if not response.HasField('protocol_version'):
    raise XgtConnectionError('Expected server protocol version.')
  return (response.protocol_version.major, response.protocol_version.minor,
          response.protocol_version.patch)

if TYPE_CHECKING:
  try:
    import pandas
  except ImportError:
    pass

# gRPC's interceptors are passed a client_call_details object which is,
# unfortunately, immutable. The interceptor API expects client_call_details to
# be passed on, but we must modify its metadata attribute en route. As such, we
# need to create an instance matching client_call_details. Unfortunately, the
# class provided by gRPC---grpc.ClientCallDetails---is supplied without a
# constructor (maybe because gRPC considers it experimental). As a result, the
# only way to modify metadata is to construct a new instance of a custom class
# which supplies the same attributes as grpc.ClientCallDetails.
# This is that class. It uses namedtuple to provide four fixed attributes.
class _ClientCallDetails(
    collections.namedtuple(
        '_ClientCallDetails',
        ('method', 'timeout', 'metadata', 'credentials')),
    grpc.ClientCallDetails):
  pass

# Represents the default namespace value.
class _DefaultNamespace:
  pass

class SessionTokenClientInterceptor(grpc.UnaryUnaryClientInterceptor,
                                    grpc.StreamUnaryClientInterceptor,
                                    grpc.UnaryStreamClientInterceptor):
  """
  Interceptor that inserts the session token into the metadata to be
  authenticated by the server.
  """
  def __init__(self):
    self._token = None

  def _intercept_call(self, continuation, client_call_details,
                      request_or_iterator):
    metadata = []
    if client_call_details.metadata is not None:
      metadata = list(client_call_details.metadata)
    metadata.append(('session_token', self._token))
    client_call_details = _ClientCallDetails(
        client_call_details.method, client_call_details.timeout, metadata,
        client_call_details.credentials)
    response = continuation(client_call_details, request_or_iterator)
    return response

  def intercept_unary_unary(self, continuation, client_call_details, request):
    return self._intercept_call(continuation, client_call_details, request)

  def intercept_stream_unary(self, continuation,
                             client_call_details, request_iterator):
    return self._intercept_call(continuation, client_call_details,
                                request_iterator)

  def intercept_unary_stream(self, continuation, client_call_details, request):
    return self._intercept_call(continuation, client_call_details, request)

  def _set_token(self, token):
    self._token = token

  def get_token(self):
    return self._token

class ArrowBasicClientAuthHandler(pyarrow.flight.ClientAuthHandler):
  def __init__(self, token = ''):
    super().__init__()
    self.token = token
    if self.token != '':
      self.basic_auth = pyarrow.flight.BasicAuth('#existing_token', self.token)
    else:
      raise XgtConnectionError('Expected non-empty token for Arrow auth')

  def authenticate(self, outgoing, incoming) -> None:
    auth = self.basic_auth.serialize()
    outgoing.write(auth)
    ret_token = incoming.read()
    if ret_token != self.token.encode('utf-8'):
      raise XgtConnectionError('Expected return token to be the '
                               'same as the source')

  def get_token(self) -> str:
    return self.token

class BasicAuth(object):
  """
  Basic authentication mechanism with user id and password.

  Parameters
  ----------
  username : str
    The username to authenticate as.
  password : str
    Password used to authenticate.
  """

  def __init__(self, username : str = 'MajorTom', password : str = ''):
    """
    Constructor for BasicAuth.  Called when BasicAuth is created.
    """
    self._username = username
    self._password = password

  @property
  def username(self) -> str:
    """
    str: The username used for authentication.
    """
    return self._username

  @property
  def password(self) -> str:
    """
    str: The password used for authentication.
    """
    return self._password

class KerberosAuth(object):
  """
  Kerberos-based single-sign on authentication.

  Parameters
  ----------
    principal : str
      Value to use for the Kerberos principal name of the xGT service to
      connect to.
      Only needed when the Kerberos principal cannot be derived from the host
      name.
      The default is an empy string.
  """

  def __init__(self, principal : str = ''):
    """
    Constructor for KerberosAuth. Called when KerberosAuth is created.
    """
    self._principal = principal

  @property
  def principal(self) -> str:
    """
    str: The Kerberos principal.
    """
    return self._principal

class PKIAuth(object):
  """
  PKI-based authentication.  Will derive user ID from information in the
  required x509 client certificate.  Automatically enables mutual TLS for
  connecting to the server.

  .. versionadded:: 1.15.0

  Parameters
  ----------
    ssl_root_dir : str
      Path to the root folder for ssl certificates and private keys.
      Defaults to the user's home directory.
    ssl_server_cert : str
      File containing the certificate chain that validates the server's
      certificate.
      Defaults to ssl_root_dir + '/certs/ca-chain.cert.pem'.
    ssl_client_cert : str
      File containing the client's certificate.
      Defaults to ssl_root_dir + '/certs/client.cert.pem'
    ssl_client_key : str
      File containing the client's key.
      Defaults to ssl_root_dir + '/private/client.key.pem'

      .. versionadded:: 1.16.0
  """

  def __init__(self, ssl_root_dir : Optional[str] = None,
               ssl_server_cert : Optional[str] = None,
               ssl_client_cert : Optional[str] = None,
               ssl_client_key : Optional[str] = None):
    """
    Constructor for PKIAuth.  Called when PKIAuth is created.
    """
    if ssl_root_dir is None:
      self._ssl_root_dir = expanduser("~") + '/.ssl/'
    else:
      self._ssl_root_dir = ssl_root_dir
    if ssl_server_cert is None:
      self._ssl_server_cert = self._ssl_root_dir + '/certs/ca-chain.cert.pem'
    else:
      self._ssl_server_cert = ssl_server_cert
    if ssl_client_cert is None:
      self._ssl_client_cert = self._ssl_root_dir + '/certs/client.cert.pem'
    else:
      self._ssl_client_cert = ssl_client_cert
    if ssl_client_key is None:
      self._ssl_client_key = self._ssl_root_dir + '/private/client.key.pem'
    else:
      self._ssl_client_key = ssl_client_key

  @property
  def ssl_root_dir(self) -> str:
    """
    str: The SSL certificate directory.
    """
    return self._ssl_root_dir

  @property
  def ssl_server_cert(self) -> str:
    """
    str: The location of the file with the certificate chain validating
    the server certificate.
    """
    return self._ssl_server_cert

  @property
  def ssl_client_cert(self) -> str:
    """
    str: The location of the file with the client's certificate.
    """
    return self._ssl_client_cert

  @property
  def ssl_client_key(self) -> str:
    """
    str: The location of the file with the client's key.
    """
    return self._ssl_client_key

class ProxyPKIAuth(PKIAuth):
  """
  PKI-based authentication through a proxy.  Will derive user ID from
  information in the passed-in x509 actual client certificate.  Automatically
  enables mutual TLS for connecting to the server.

  .. versionadded:: 2.0.6

  Parameters
  ----------
    ssl_root_dir : str
      Path to the root folder for ssl certificates and private keys.
      Defaults to the user's home directory.
    ssl_server_cert : str
      File containing the certificate chain that validates the server's
      certificate.
      Defaults to ssl_root_dir + '/certs/ca-chain.cert.pem'.
    ssl_proxy_cert : str
      File containing the proxy's certificate.
    ssl_proxy_key : str
      File containing the proxy's key.
    ssl_actual_cert : str
      Contents of the actual client certificate that should be validated.
      The gRPC connection will be done under the proxy's certificate identity,
      but the logical xGT connection will correspond to the actual certificate's
      identity.
  """

  def __init__(self, ssl_root_dir : Optional[str] = None,
               ssl_server_cert : Optional[str] = None,
               ssl_proxy_cert : Optional[str] = None,
               ssl_proxy_key : Optional[str] = None,
               ssl_actual_cert : Optional[str] = None):
    super().__init__(ssl_root_dir = ssl_root_dir,
                     ssl_server_cert = ssl_server_cert,
                     ssl_client_cert = ssl_proxy_cert,
                     ssl_client_key = ssl_proxy_key)
    self._ssl_actual_cert = ssl_actual_cert

  @property
  def ssl_proxy_cert(self) -> str:
    """
    str: The location of the file with the proxy's certificate.
    """
    return self.ssl_client_cert

  @property
  def ssl_proxy_key(self) -> str:
    """
    str: The location of the file with the proxy's key.
    """
    return self.ssl_client_key

  @property
  def ssl_actual_cert(self) -> str:
    """
    str: The contents of the actual client certificate
    """
    return self._ssl_actual_cert

class TrustedProxyAuth(PKIAuth):
  """
  PKI-based authentication through a trusted proxy.  User ID is passed by
  the trusted proxy.  Automatically enables mutual TLS for connecting
  to the server.

  .. versionadded:: 2.3.0

  Parameters
  ----------
    ssl_root_dir : str
      Path to the root folder for ssl certificates and private keys.
      Defaults to the user's home directory.
    ssl_server_cert : str
      File containing the certificate chain that validates the server's
      certificate.
      Defaults to ssl_root_dir + '/certs/ca-chain.cert.pem'.
    ssl_proxy_cert : str
      File containing the proxy's certificate.
    ssl_proxy_key : str
      File containing the proxy's key.
    userid : str
      User ID coming from the trusted proxy.  The gRPC connection will
      be done under the proxy's certificate identity, but the logical
      xGT connection will correspond to this user ID.
  """

  def __init__(self, ssl_root_dir : Optional[str] = None,
               ssl_server_cert : Optional[str] = None,
               ssl_proxy_cert : Optional[str] = None,
               ssl_proxy_key : Optional[str] = None,
               userid : Optional[str] = None):
    super().__init__(ssl_root_dir = ssl_root_dir,
                     ssl_server_cert = ssl_server_cert,
                     ssl_client_cert = ssl_proxy_cert,
                     ssl_client_key = ssl_proxy_key)
    self._userid = userid

  @property
  def ssl_proxy_cert(self) -> str:
    """
    str: The location of the file with the proxy's certificate.
    """
    return self.ssl_client_cert

  @property
  def ssl_proxy_key(self) -> str:
    """
    str: The location of the file with the proxy's key.
    """
    return self.ssl_client_key

  @property
  def userid(self) -> str:
    """
    str: The user ID provided by the proxy.
    """
    return self._userid

class SessionKeepAliveTask:
  def __init__(self, time_interval, admin_svc):
    self._running = True
    self._cv = threading.Condition()
    self._time_interval = time_interval
    self._admin_svc = admin_svc

  def terminate(self) -> None:
    self._running = False
    with self._cv:
      # The cv variable needs to be locked which
      # is a slightly different behavior from c/c++.
      self._cv.notify_all()

  def run(self) -> None:
    while self._running:
      with self._cv:
        try:
          request = admin_proto.KeepAliveSessionRequest()
          self._admin_svc.KeepAliveSession(request)
        except grpc.RpcError:
          pass
        self._cv.wait(self._time_interval)

class Connection(object):
  """
  Connection to the server with functionality to create, change, and remove
  graph structures and run jobs.

  Parameters
  ----------
  host : str
    IP address of the computer where the server is running.
  port : int
    Port where the server is listening on for RPC calls.
  auth : BasicAuth, KerberosAuth, PKIAuth, ProxyPKIAuth or TrustedProxyAuth.
    Instance of the authentication mechanism to use.  Can be BasicAuth,
    KerberosAuth, PKIAuth, ProxyPKIAuth or TrustedProxyAuth.
    Default is BasicAuth with no parameters.

    .. versionadded:: 1.11.0
  flags: dict
    Dictionary containing flags.  Possible flags are:

    aws_access_key_id : str
      Amazon Access Key ID, used for authentication when loading data
      files from S3 buckets.  The default is an empty string.
    aws_secret_access_key : str
      Amazon Access Key ID, used for authentication when loading data
      files from S3 buckets.  The default is an empty string.
    aws_session_token : str
      Amazon Session Token, used for authentication when loading data
      files from S3 buckets.  The default is an empty string.
    ssl : boolean
      If true use ssl authentication for secure server channels.
      The default is False.
    ssl_root_dir : str
      Path to the root folder for ssl certificates and private keys.
      Defaults to the user's home directory.
    ssl_server_cn : str
      The Common Name (CN) on the certificate of the server to connect to.
      The default is the hostname.
    ssl_server_cert : str
      File containing the certificate chain that validates the server's
      certificate.
      Defaults to ssl_root_dir + '/certs/ca-chain.cert.pem'.

      .. versionadded:: 1.11.0
    ssl_use_mtls : bool
      Indicates whether to use the mutual TLS protocol.  The client must provide
      certificates validating its identity under ssl_root_dir.
      Defaults to False.

      .. versionadded:: 1.11.0
    ssl_client_cert : str
      File containing the client's certificate.
      Defaults to ssl_root_dir + '/certs/client.cert.pem'
    ssl_client_key : str
      File containing the client's key.
      Defaults to ssl_root_dir + '/private/client.key.pem'

      .. versionadded:: 1.16.0
  """

  _GIB = 1024 * 1024 * 1024

  def __init__(self, host : str ='127.0.0.1', port : int = 4367,
               flags : Optional[dict] = None, auth :
               Union[BasicAuth, KerberosAuth, PKIAuth,
                     ProxyPKIAuth, TrustedProxyAuth] = BasicAuth()):
    """
    Constructor for Connection.  Called when Connection is created.
    """
    self._init_helper(host, port, flags, auth)
    self._default_namespace = None
    self.set_default_namespace(_DefaultNamespace())
    self._default_graph = None
    self._arrow_init_helper(host, port)

  def _init_helper(self, host, port, flags, auth):
    if flags is None:
      flags = {}
    self.port = port
    self.aws_access_key_id = flags.get('aws_access_key_id', '')
    self.aws_secret_access_key = flags.get('aws_secret_access_key', '')
    self.aws_session_token = flags.get('aws_session_token', '')
    self.proxy_pki = False
    self.trusted_proxy = False

    if isinstance(auth, PKIAuth):
      self.ssl_root_dir = auth.ssl_root_dir
      self.ssl_server_cert = auth.ssl_server_cert
      self.ssl_client_cert = auth.ssl_client_cert
      self.ssl_client_key = auth.ssl_client_key
      # Forces the use of SSL for PKI authentication
      self.ssl = True
      # Must use mutual TLS for PKI authentication.
      self.ssl_use_mtls = True
      self.use_pki = True
      if isinstance(auth, ProxyPKIAuth):
        self.proxy_pki = True
      if isinstance(auth, TrustedProxyAuth):
        self.trusted_proxy = True
        self.proxy_pki = False
    else:
      self.ssl = flags.get('ssl', False)
      self.ssl_root_dir = flags.get('ssl_root_dir', expanduser("~") + '/.ssl/')
      self.ssl_use_mtls = flags.get('ssl_use_mtls', False)
      self.use_pki = False
      self.ssl_server_cert = flags.get('ssl_server_cert',
                                       self.ssl_root_dir +
                                       '/certs/ca-chain.cert.pem')
      self.ssl_client_cert = flags.get('ssl_client_cert',
                                       self.ssl_root_dir +
                                       '/certs/client.cert.pem')
      self.ssl_client_key = flags.get('ssl_client_key',
                                      self.ssl_root_dir +
                                      '/private/client.key.pem')

    self.ssl_server_cn = flags.get('ssl_server_cn', host)
    self.kerberos = isinstance(auth, KerberosAuth)
    if self.kerberos:
      self.krb_principal = auth.principal
    else:
      self.krb_principal = None
    self.host = host
    self.cwd = os.getcwd()

    self._metadata_interceptor = SessionTokenClientInterceptor()
    self._channel = self._create_channel()
    self._admin_svc = admin_grpc.AdminServiceStub(self._channel)
    self._data_svc = data_grpc.DataServiceStub(self._channel)
    self._graph_svc = graph_grpc.GraphTypesServiceStub(self._channel)
    self._job_svc = job_grpc.JobServiceStub(self._channel)
    self._metrics_svc = metrics_grpc.MetricsServiceStub(self._channel)
    # Ping the server every 30 minutes to keep alive the session.
    session_ping = SessionKeepAliveTask(1800, self._admin_svc)
    session_ping_thread = threading.Thread(target = session_ping.run)
    # Detach this thread so it doesn't block ending the program.
    # We terminate and join against it at the end anyway during cleanup.
    session_ping_thread.daemon = True
    # Set the user ID to the empty string.
    self._userid = ''
    self._is_admin = None

    # Close outstanding session on destruction of this instance with a closure.
    admin_svc = self._admin_svc  # Break self dependency on weakref.
    def cleanup():
      session_ping.terminate()
      try:
        request = admin_proto.CloseSessionRequest()
        admin_svc.CloseSession(request)
      except grpc.RpcError:
        pass
      if session_ping_thread.is_alive():
        session_ping_thread.join()

    weakref.finalize(self, cleanup)

    if not self.kerberos and not self.use_pki:
      self._request_session_token(auth.username, auth.password)
    else:
      if self.kerberos or (not self.proxy_pki and not self.trusted_proxy):
        # This is the path for Kerberos or regular PKI.
        self._request_session_token('', '')
      if self.proxy_pki:
        # This is the path for proxy PKI with a client cert.
        self._request_session_token('', auth.ssl_actual_cert)
      if self.trusted_proxy:
        # This is the path for a trusted proxy with just a user ID and a
        # validated IP address.
        self._request_session_token(auth.userid, '')

    if self.kerberos:
      import gssapi
      # Check that the principal is non-empty before doing anything else.
      if self.krb_principal is None or self.krb_principal == '':
        # This is a valid default principal if the server is configured as part
        # of the Kerberos realm.
        self.krb_principal = 'xgtd/' + host
      if not isinstance(self.krb_principal, str):
        raise XgtConnectionError('Expected a valid string principal for '
                                 'Kerberos')
      # Start the Kerberos authentication process
      server_name = gssapi.Name(self.krb_principal)
      client_context = gssapi.SecurityContext(name = server_name,
                                              usage = 'initiate')
      self._krb_auth_helper(client_context)
    session_ping_thread.start()

  def _arrow_init_helper(self, host, port):
    # Arrow End point connection
    if (self.ssl):
      chain_cert = open(self.ssl_server_cert, 'rb').read()

      if (self.ssl_use_mtls):
        client_key = open(self.ssl_client_key, 'rb').read()
        client_cert = open(self.ssl_client_cert, 'rb').read()
        self.arrow_conn = pyarrow.flight.FlightClient((host, port),
                                                      tls_root_certs=chain_cert,
                                                      cert_chain=client_cert,
                                                      private_key=client_key,
                                                      override_hostname=
                                                      self.ssl_server_cn)
      else:
        self.arrow_conn = pyarrow.flight.FlightClient((host, port),
                                                      tls_root_certs=chain_cert,
                                                      override_hostname=
                                                      self.ssl_server_cn)
    else:
      self.arrow_conn = pyarrow.flight.FlightClient((host, port))

    self.arrow_conn.authenticate(
        ArrowBasicClientAuthHandler(self._metadata_interceptor.get_token()))

  def _krb_auth_helper(self, client_context):
    # Note that we already have obtained the session token from the initial gRPC
    # handshake.
    client_token = client_context.step()
    session_token = self._metadata_interceptor.get_token()
    while not client_context.complete:
      request = admin_proto.KerberosAuthenticateRequest()
      request.session_token = session_token
      request.krb_token = client_token
      _add_version_number(request)
      response = self._call(request, self._admin_svc.KerberosAuthenticate)
      _check_version_number(response)
      client_token = client_context.step(response.krb_token)

    # We have established an authenticated context with the server.  Now send
    # the final auth message and verify that the server returns the correct
    # signature for it.
    orig_msg = session_token.encode('utf-8')
    wrapped_msg, _ = client_context.wrap(orig_msg, True)
    request = admin_proto.KerberosAuthenticateRequest()
    request.session_token = session_token
    request.krb_token = wrapped_msg
    _add_version_number(request)
    response = self._call(request, self._admin_svc.KerberosAuthenticate)
    _check_version_number(response)
    client_context.verify_signature(orig_msg, response.krb_token)
    if response.userid != '':
      self._userid = response.userid

  def _create_channel(self):
    channel = None
    connection_string = f'{self.host}:{self.port}'
    if (self.ssl):
      chain_cert = open(self.ssl_server_cert, 'rb').read()

      if (self.ssl_use_mtls):
        client_key = open(self.ssl_client_key, 'rb').read()
        client_cert = open(self.ssl_client_cert, 'rb').read()
        channel_credentials = grpc.ssl_channel_credentials(chain_cert,
                                                           client_key,
                                                           client_cert)
      else:
        channel_credentials = grpc.ssl_channel_credentials(chain_cert)
      try:
        channel = grpc.secure_channel(
            connection_string, channel_credentials,
            options=(('grpc.ssl_target_name_override', self.ssl_server_cn,),
                     ('grpc.max_send_message_length', -1),
                     ('grpc.max_receive_message_length', -1),)
        )
      except grpc.RpcError as ex:
        raise XgtConnectionError(ex.details, '')
    else:
      try:
        channel = grpc.insecure_channel(connection_string,
            options=(('grpc.max_send_message_length', -1),
                     ('grpc.max_receive_message_length', -1),)
        )
      except grpc.RpcError as ex:
        raise XgtConnectionError(ex.details, '')
    return grpc.intercept_channel(channel, self._metadata_interceptor)

  # Authenticate and request a session token that persists for the lifetime of
  # the session.
  def _request_session_token(self, userid, credentials):
    self.server_protocol = None
    try:
      request = admin_proto.ProtocolVersionRequest()
      _add_version_number(request)
      response = self._call(request, self._admin_svc.ProtocolVersion)
      self.server_protocol = _check_version_number(response)
    except Exception as e:
        pass
    # Store the server's capabilities offered by its protocol version.
    self.capabilities_bitmap = _process_protocol_version(
        self.server_protocol, __protobuf_version__)

    try:
      if not self.kerberos and not self.use_pki:
        request = admin_proto.AuthenticateRequest()
        request.userid = userid
        request.credentials = credentials
        _add_version_number(request)
        response = self._call(request, self._admin_svc.Authenticate)
        _check_version_number(response)
      elif not self.kerberos:
        request = admin_proto.AuthenticateRequest()
        _add_version_number(request)
        if credentials != '':
          request.pki_cert = credentials
          response = self._call(request, self._admin_svc.ProxyPKIAuthenticate)
        elif self.trusted_proxy:
          # Verify that the server does support trusted proxy auth.
          if not (self.capabilities_bitmap & TRUSTED_PROXY):
            raise XgtNotImplemented(
              "The xGT server's version is not new enough to support trusted " +
              "proxy authentication. This feature requires version 2.3 or " +
              "later.")
          request.userid = userid
          response = self._call(request, self._admin_svc.TrustedProxyAuthenticate)
        else:
          response = self._call(request, self._admin_svc.PKIAuthenticate)
          _check_version_number(response)
      else:
        request = admin_proto.KerberosAuthenticateRequest()
        request.krb_token = credentials.encode('utf-8')
        _add_version_number(request)
        response = self._call(request, self._admin_svc.KerberosAuthenticate)
        _check_version_number(response)
      self._metadata_interceptor._set_token(response.session_token)
      if response.userid != '':
        self._userid = response.userid
      else:
        self._userid = userid
    except Exception as e:
      raise XgtConnectionError(f'Failure on session token request: {e}')

  def _call(self, request, rpc_function):
    try:
      response = rpc_function(request)
    except grpc.RpcError as ex:
      raise XgtConnectionError(ex.details, '')
    try:
      _ = iter(response)
      # For streaming responses that return an iterator, it is the caller's
      # responsibility to check each packet for errors. E.g.:
      #   for result in response:
      #     _assert_noerrors(result)
      # If the response is non-streaming (i.e. not an iterable object), the
      # response is checked for errors below.
      return response
    except TypeError:
      pass
    _assert_noerrors(response)
    return response

  def _change_exit_error_count(self, action):
    action_u = action.upper()
    request = admin_proto.ChangeErrorCountRequest()
    request.action = admin_proto.ErrorCountActionEnum.Value(action_u)
    response = self._call(request, self._admin_svc.ChangeErrorCount)
    return response.error_count

  def _process_kwargs(self, request, args_to_expand):
    for k,v in args_to_expand.items():
      if v is not None:
        if isinstance(v, bool):
          request.kwargs[k].bool_value = v
        elif isinstance(v, int):
          request.kwargs[k].int_value = v
        elif isinstance(v, float):
          request.kwargs[k].float_value = v
        elif isinstance(v, str):
          request.kwargs[k].string_value = v

  def _process_parameter(self, request, k, v):
    newValue = admin_proto.Parameter()
    if isinstance(v, bool):
      newValue.bool_value = v
    elif isinstance(v, int):
      newValue.int_value = v
    elif isinstance(v, float):
      newValue.float_value = v
    elif isinstance(v, Decimal):
      if (v % 1 == 0):
        newValue.int_value = int(v)
      else:
        newValue.float_value = float(v)
    elif isinstance(v, str):
      newValue.string_value = v
    elif isinstance(v, datetime_time):
      newValue.time_value.value = str(v)
    elif isinstance(v, datetime):
      newValue.datetime_value.value = str(v)
    elif isinstance(v, date):
      newValue.date_value.value = str(v)
    elif isinstance(v, timedelta):
      newValue.duration_value.value = str(v)
    elif isinstance(v, (IPv4Address, IPv6Address)):
      newValue.ipaddress_value.value = str(v)
    elif isinstance(v, RowID):
      newValue.row_id_value.row_id = v._row_id
      newValue.row_id_value.validation_id = v._validation_id
    else:
      raise TypeError("Parameter value {v} is not a supported type.")
    request.parameters[k].value.extend([newValue])

  def _process_parameters(self, request, args_to_expand):
    for k, v in args_to_expand.items():
      if isinstance(v, list):
        for item in v:
          self._process_parameter(request, k, item)
      else:
        self._process_parameter(request, k, v)

  def _launch_job(self, query, **kwargs):
    if not isinstance(query, str):
      raise TypeError(f"Unexpected argument type '{type(query)}'")
    if 'optlevel' in kwargs:
      _validate_opt_level(kwargs['optlevel'])

    request = job_proto.ScheduleJobsCypherRequest()
    request.cypher_query.extend([query])
    if 'parameters' in kwargs and kwargs['parameters'] != None:
      self._process_parameters(request, kwargs['parameters'])
    if 'use_gql' in kwargs:
      request.use_gql = kwargs['use_gql']
    self._process_kwargs(request, kwargs)
    response = self._call(request, self._job_svc.ScheduleJobsCypher)
    one_job = response.job_status[0]
    return Job(self, one_job)

  def _compile_query_helper(self, query, **kwargs):
    if not isinstance(query, str):
      raise TypeError(f"Unexpected argument type '{type(query)}'")
    if 'optlevel' in kwargs:
      _validate_opt_level(kwargs['optlevel'])

    request = job_proto.CompileQueryRequest()
    request.query = query
    if 'parameters' in kwargs and kwargs['parameters'] != None:
      self._process_parameters(request, kwargs['parameters'])
    self._process_kwargs(request, kwargs)
    response = self._call(request, self._job_svc.CompileQuery)

  def _compile_query(self, query : str, parameters : Mapping = None,
                     optlevel : int = 4):
    self._compile_query_helper(query, optlevel = optlevel,
                               parameters = parameters)

  #------------------------- Housekeeping Methods
  @property
  def server_version(self) -> str:
    """
    str: The current server version.
    """
    request = admin_proto.VersionRequest()
    response = self._call(request, self._admin_svc.Version)
    return response.version

  @property
  def max_user_memory_size(self) -> float:
    """
    float: The maximum amount of memory available for user data on the xGT
    server.  In gibibytes.
    """
    request = admin_proto.MaxUserMemorySizeRequest()
    response = self._call(request, self._admin_svc.MaxUserMemorySize)
    return response.pool_size / Connection._GIB

  @property
  def free_user_memory_size(self) -> float:
    """
    float: The amount of free memory available for user data on the xGT server.
    In gibibytes.
    """
    request = admin_proto.FreeUserMemorySizeRequest()
    response = self._call(request, self._admin_svc.FreeUserMemorySize)
    return response.free_memory_size / Connection._GIB

  @property
  def userid(self) -> str:
    """
    str: The identity of the connected user.
    """
    return self._userid

  @property
  def is_admin(self) -> bool:
    """
    bool: True if the user is an administrator.

    .. versionadded:: 2.0.6
    """
    if self._is_admin is None:
      request = admin_proto.IsAdminRequest()
      response = self._call(request, self._admin_svc.IsAdmin)
      self._is_admin = response.is_admin

    return self._is_admin

  @property
  def expiration_date(self) -> str:
    """
    str: The license expiration date.

    .. versionadded:: 2.0.6
    """
    request = admin_proto.VersionRequest()
    response = self._call(request, self._admin_svc.Version)
    return response.expiration_date

  #------------------------- Catalog Getter Methods

  def get_frames(
      self, names : Optional[Iterable[str]] = None,
      namespace : Optional[str] = None,
      frame_type : Optional[str] = None) -> list[Union[EdgeFrame, VertexFrame,
                                                       TableFrame, GraphFrame]]:
    """
    Get a list of Frame objects that correspond to each frame in the xGT server.
    Only frames that the calling user has permission to read are returned.

    A specific frame object allows for interaction with a frame present in the
    xGT server.

    .. versionadded:: 1.14.0

    Parameters
    ----------
    names : list of str or None
      The names of the frames to retrieve.  Each name must be a valid frame
      name.  The namespace is optional and will use the default if none is
      given.  If None and the parameter namespace is None, all frames are
      returned.
    namespace: str or None
      Returns all frames in this namespace.  At most one of names and namespace
      can be a value other than None.
    frame_type : str
      Selects the frame type returned: Edge, Vertex, Table or Graph.  Must be
      one of 'edge', 'vertex', 'table', 'graph' or None.  If None is selected it
      will return all types.

    Returns
    -------
    list[EdgeFrame | VertexFrame | TableFrame | GraphFrame]
      Frame objects for the requested frames.

    Raises
    ------
    XgtNameError
      If a frame name requested does not exist or is not visible to the user.
      If a frame or namespace name does not follow naming rules.
    XgtTransactionError
      If a conflict with another transaction occurs.
    """
    if names is None:
      names = []
    elif not isinstance(names, Iterable) or isinstance(names, str):
      raise TypeError('Invalid argument: "names" must be a list of strings')
    else:
      names = [_validated_frame_name(n) for n in names]

    if len(names) > 0 and namespace is not None:
      raise ValueError('Only one of "names" and "namespaces" should be passed.')

    request = graph_proto.GetFramesMetadataRequest()
    if names is not None:
      request.name.extend(names)
    if namespace is not None:
      request.namespace_name = _validated_namespace_name(namespace)

    # Ignore format case.
    lc_frame_type = None if frame_type is None else frame_type.lower()
    if lc_frame_type == 'table':
      response = self._call(request, self._graph_svc.GetTableFrames)
    elif lc_frame_type == 'edge':
      response = self._call(request, self._graph_svc.GetEdgeFrames)
    elif lc_frame_type == 'vertex':
      response = self._call(request, self._graph_svc.GetVertexFrames)
    elif lc_frame_type == 'graph':
      response = self._call(request, self._graph_svc.GetGraphs)
    elif lc_frame_type is None:
      response = self._call(request, self._graph_svc.GetFrames)
    else:
      raise ValueError('frame_type must be one of edge, vertex, table graph or '
                       f'None, given: {format}')

    frames = []
    for data in response.container:
      schema = self._translate_schema_from_server(data.schema)
      if data.type == sch_proto.FrameTypeEnum.Value('TABLE'):
        frames.append(TableFrame(self, data.name, schema,
                                 data.container_id, data.commit_id))
      elif data.type == sch_proto.FrameTypeEnum.Value('EDGE'):
        frames.append(EdgeFrame(self, data.name, schema,
                                data.source_vertex, data.target_vertex,
                                data.source_key, data.target_key,
                                data.container_id, data.commit_id))
      elif data.type == sch_proto.FrameTypeEnum.Value('VERTEX'):
        frames.append(VertexFrame(self, data.name, schema, data.vertex_key,
                                  data.container_id, data.commit_id))
      elif data.type == sch_proto.FrameTypeEnum.Value('ASSOCIATIVE'):
        frames.append(GraphFrame(self, data.name, data.container_id))

    return frames

  def get_frame(
      self, name : str) -> Union[EdgeFrame, VertexFrame, TableFrame, GraphFrame]:
    """
    Get a frame object that allows interaction with a frame present in the xGT
    server.

    .. versionadded:: 1.14.0

    Parameters
    ----------
    name : str
      The names of the frame to retrieve.  Must be a valid frame name.  The
      namespace is optional, and if not given it will use the default namespace.

    Returns
    -------
    EdgeFrame | VertexFrame | TableFrame | GraphFrame
      Frame object for the requested frames.

    Raises
    ------
    XgtNameError
      If the frame requested does not exist or is not visible to the user.
    XgtTransactionError
      If a conflict with another transaction occurs.
    """
    frames = self.get_frames([name])
    if len(frames) == 0:
      raise XgtNameError(f"Frame not found: {name}. It either does not "
                         "exist or the user lacks permission to read it")
    return frames[0]

  def get_namespaces(self) -> list[str]:
    """
    Get a list of namespaces present in the xGT server.

    Returns
    -------
    list
      Names of namespaces present in the server.

    Examples
    --------
    >>> conn = xgt.Connection()
    >>> namespaces = conn.get_namespaces()
    >>> for ns in namespaces:
    >>> ... conn.drop_namespace(ns)
    """

    request = graph_proto.GetNamespacesRequest()
    response = self._call(request, self._graph_svc.GetNamespaces)
    return list(response.namespace_name)

  def get_graphs(self) -> list[str]:
    """
    Get a list of graphs present in the xGT server that the user has access to.

    Returns
    -------
    list
      Names of graphs present in the server that the user can access.

    Examples
    --------
    >>> conn = xgt.Connection()
    >>> graphs = conn.get_graphs()
    >>> for graph in graphs:
    >>> ... print (graph)

    .. experimental:: The API of this method may change in future releases.
    """

    request = graph_proto.GetFramesMetadataRequest()
    response = self._call(request, self._graph_svc.GetGraphs)
    return [data.name for data in response.container]

  #------------------------- DDL Methods
  def _container_labels_helper(self, request, frame_labels, row_label_universe):
    if frame_labels is not None:
      for access in frame_labels:
        access_lower = access.lower()
        if access_lower not in ["create", "read", "update", "delete"]:
          raise XgtValueError(f"Invalid security access type: {access}")

        for l in frame_labels[access]:
          request.frame_label_map.access_labels[access_lower].label.append(l)

    if row_label_universe is not None:
      for label in row_label_universe:
        if isinstance(label, str):
          request.row_label_universe.label.append(label)
        else:
          raise TypeError('Invalid argument: row labels must be strings')

    return request

  def _create_namespace_helper(self, name, frame_labels, row_label_universe,
                               attempts, conditional):
    request = graph_proto.CreateNamespaceRequest()
    request.name = _validated_namespace_name(name)
    request.conditional_create = conditional
    request = self._container_labels_helper(request, frame_labels,
                                            row_label_universe)
    self._process_kwargs(request, {'attempts':attempts})
    self._call(request, self._graph_svc.CreateNamespace)

  def create_namespace(
      self, name : str,
      frame_labels : Optional[Mapping[str, Sequence[str]]] = None,
      row_label_universe : Optional[Iterable[str]] = None,
      attempts : int = 1) -> None:
    """
    Create a new empty namespace on the server.

    Parameters
    ----------
    name : str
      The name of the namespace to create.
    frame_labels : dictionary
      The permissions to apply to the namespace.  Given as a dictionary mapping
      a string to a list of strings.  The key represents the permission type.
      The value represents the labels required for this permission.  Permission
      types are "create", "read", "update", and "delete".  By default, no labels
      are required.
    row_label_universe : Iterable of strs
      All possible labels to be used for rows inside this namespace.  A maximum
      of 128 labels are supported for rows in each frame.  By default, no row
      labels are required.

      **NOT yet supported**.
    attempts : int
      Number of times to attempt the creation of the namespace.
      It will be retried if it fails due to transactional conflicts.

    Raises
    ------
    XgtNameError
      If the name provided does not follow rules for namespace names.
      A namespace name cannot contain "__", which is used as a separator
      between namespace and name in fully qualified frame names.
      If a namespace with this name already exists.
    XgtSecurityError
      If the user does not have required permissions for this action.
    XgtTransactionError
      If a conflict with another transaction occurs.

    Examples
    --------
    >>> import xgt
    >>> conn = xgt.Connection()
    >>> labels = { 'create' : ['label1', 'label2'],
    ...            'read' : ['label1'],
    ...            'update' : ['label1'],
    ...            'delete' : ['label1', 'label2', 'label3'] }
    >>> row_label_universe = [ 'label1', 'label4' ]
    >>> conn.create_namespace('career', labels, row_label_universe)
    """
    self._create_namespace_helper(name, frame_labels, row_label_universe,
                                  attempts, False)

  def create_graph(
      self, name : str,
      graph_members : Union[dict[str, Union[str, VertexFrame, EdgeFrame]],
                            set[Union[str, VertexFrame, EdgeFrame]]],
      frame_labels : Optional[Mapping[str, Sequence[str]]] = None,
      row_label_universe : Optional[Iterable[str]] = None,
      attempts : int = 1) -> GraphFrame:
    """
    Create a new graph on the server.  If a frame is given without an alias, it
    is given an alias of its fully qualified name.

    Parameters
    ----------
    name : str
      The fully qualified name of the graph to create.
    graph_members : dict[str | VertexFrame | EdgeFrame] | set[str | VertexFrame | EdgeFrame]
      The frames to add to the graph.  Given as either a dictionary mapping
      aliases to frames or a set of frames.  Frames can be given as either a
      frame name or object.
    frame_labels : Mapping[str, Sequence[str]] | None
      The permissions to apply to the graph.  Given as a dictionary mapping a
      string to a list of strings.  The key represents the permission type.  The
      value represents the labels required for this permission.  Permission
      types are "create", "read", "update", and "delete".  By default, no labels
      are required.
    row_label_universe : Iterable[str] | None
      All possible labels to be used for rows inside this graph.  A maximum of
      128 labels are supported for rows in each frame.  By default, no row
      labels are required.

      **NOT yet supported**.
    attempts : int
      Number of times to attempt the creation of the namespace.
      It will be retried if it fails due to transactional conflicts.

    Returns
    -------
    GraphFrame
      Frame to the graph.

    Raises
    ------
    XgtNameError
      If the name provided is not a correct frame name or a frame with this
      name already exists in the namespace.
    XgtSecurityError
      If the user does not have required permissions for this action.
    XgtTransactionError
      If a conflict with another transaction occurs.
    XgtTypeError
      If a frame specified as a graph member is not a vertex or edge frame.

    Examples
    --------
    >>> import xgt
    >>> conn = xgt.Connection()
    >>> labels = { 'create' : ['label1', 'label2'],
    ...            'read' : ['label1'],
    ...            'update' : ['label1'],
    ...            'delete' : ['label1', 'label2', 'label3'] }
    >>> conn.create_graph('graph',
                          { 'v0' : 'Vertex0', 'v1' : 'other__Vertex0',
                            'edge' : 'Edge' }, labels)

    .. experimental:: The API of this method may change in future releases.
    """
    request = graph_proto.CreateGraphRequest()
    request.name = _validated_frame_name(name)
    request.conditional_create = False
    request = self._container_labels_helper(request, frame_labels,
                                            row_label_universe)
    for alias, frame in _process_graph_members(graph_members).items():
      request.frames[alias] = frame
    self._process_kwargs(request, {'attempts':attempts})
    response = self._call(request, self._graph_svc.CreateGraph)
    data = response.container[0]
    return GraphFrame(self, data.name, data.container_id)

  def create_table_frame(
      self, name : str, schema : list[list],
      frame_labels : Optional[Mapping[str, Sequence[str]]] = None,
      row_label_universe : Optional[Sequence] = None,
      attempts : int = 1) -> TableFrame:
    """
    Create a new TableFrame in the server.

    A TableFrame represents a table held on the xGT server whose rows share the
    same property names and types.  This function creates a new frame of
    vertices on the xGT server and returns a VertexFrame representing it.

    Parameters
    ----------
    name : str
      Name of the frame.  Must be a valid frame name.  The namespace is
      optional, and if not given the default namespace will be used.
    schema : list of lists
      The schema defining the property names and types.  Each row in the frame
      will have these properties.  Given as a list of lists associating property
      names with xGT data types.
    frame_labels : dictionary
      The permissions to apply to the frame.  Given as a dictionary mapping a
      string to a list of strings.  The key represents the permission type.  The
      value represents the labels required for this permission.  Permission
      types are "create", "read", "update", and "delete".  By default, no labels
      are required.
    row_label_universe : Iterable of strs
      All possible labels to be used for rows inside this frame.  A maximum of
      128 labels are supported for rows in each frame.  By default, no row
      labels are required.
    attempts : int
      Number of times to attempt the creation of the TableFrame.  The creation
      will be retried if it fails due to transactional conflicts.

    Returns
    -------
    TableFrame
      Frame to the table.

    Raises
    ------
    XgtNameError
      If the name provided is not a correct frame name or
      a frame with this name already exists in the namespace.
    XgtSecurityError
      If the user does not have required permissions for this action.
    XgtTransactionError
      If a conflict with another transaction occurs.

    Examples
    --------
    >>> import xgt
    >>> conn = xgt.Connection()
    >>> conn.create_table_frame(
    ...   name = 'Table1',
    ...   schema = [['id', xgt.INT],
    ...             ['name', xgt.TEXT]],
    ...   frame_labels = { 'create' : ['label1'],
    ...                    'delete' : ['label1', 'label2'] })
    """
    name = _validated_frame_name(name)
    schema = _validated_schema(schema)

    request = graph_proto.CreateFrameRequest()
    request.type = sch_proto.FrameTypeEnum.Value('TABLE')
    request.name = name

    _generate_proto_schema_from_xgt_schema(request, schema)

    request = self._container_labels_helper(request, frame_labels,
                                            row_label_universe)

    self._process_kwargs(request, {'attempts':attempts})
    response = self._call(request, self._graph_svc.CreateFrame)

    data = response.container[0]
    schema = self._translate_schema_from_server(data.schema)
    frame = TableFrame(self, data.name, schema,
                       data.container_id, data.commit_id)
    return frame

  def create_vertex_frame(
      self, name : str, schema : list[list], key : str,
      frame_labels : Optional[Mapping[str, Sequence[str]]] = None,
      row_label_universe : Optional[Sequence] = None,
      attempts : int = 1) -> VertexFrame:
    """
    Create a new VertexFrame in the server.

    A VertexFrame represents a collection of vertices held on the xGT server
    that share the same property names and types.  This function creates a new
    frame of vertices on the xGT server and returns a VertexFrame representing
    it.

    Each vertex in the frame must have a key property that uniquely identifies
    the vertex.  The key parameter gives the schema property that is the key.

    Parameters
    ----------
    name : str
      Name of the frame.  Must be a valid frame name.  The namespace is
      optional, and if not given the default namespace will be used.
    schema : list of lists
      The schema defining the property names and types.  Each row in the frame
      will have these properties.  Given as a list of lists associating property
      names with xGT data types.
    key : str
      The property name used to uniquely identify vertices in the graph.  This
      is the name of one of the properties from the schema and must be unique
      for each vertex in the frame.
    frame_labels : dictionary
      The permissions to apply to the frame.  Given as a dictionary mapping a
      string to a list of strings.  The key represents the permission type.  The
      value represents the labels required for this permission.  Permission
      types are "create", "read", "update", and "delete".  By default, no labels
      are required.
    row_label_universe : Iterable of strs
      All possible labels to be used for rows inside this frame.  A maximum of
      128 labels are supported for rows in each frame.  By default, no row
      labels are required.
    attempts : int
      Number of times to attempt the creation of the VertexFrame.  The creation
      will be retried if it fails due to transactional conflicts.

    Returns
    -------
    VertexFrame
      Frame to the collection of vertices.

    Raises
    ------
    XgtNameError
      If the name provided is not a correct frame name.
      If the key is not in the schema.
      If a frame with this name already exists in the namespace.
    XgtSecurityError
      If the user does not have required permissions for this action.
    XgtTransactionError
      If a conflict with another transaction occurs.

    Examples
    --------
    >>> import xgt
    >>> conn = xgt.Connection()
    >>> people = conn.create_vertex_frame(
    ...            name = 'People',
    ...            schema = [['id', xgt.INT],
    ...                      ['name', xgt.TEXT]],
    ...            key = 'id',
    ...            frame_labels = { 'create' : ['label1'],
    ...                             'delete' : ['label1', 'label2'] })
    """
    name = _validated_frame_name(name)
    schema = _validated_schema(schema)
    key = _validated_property_name(key)
    num_columns = len(schema)

    key_col = num_columns
    for col in range(num_columns):
      if schema[col][0] == key:
        key_col = col

    if key_col == num_columns:
      raise XgtNameError(f'The vertex key "{key}" does not match any schema '
                         'property name in this frame.')

    request = graph_proto.CreateFrameRequest()
    request.type = sch_proto.FrameTypeEnum.Value('VERTEX')
    request.name = name
    request.vertex_key = key_col

    _generate_proto_schema_from_xgt_schema(request, schema)

    request = self._container_labels_helper(request, frame_labels,
                                            row_label_universe)

    self._process_kwargs(request, {'attempts':attempts})
    response = self._call(request, self._graph_svc.CreateFrame)

    data = response.container[0]
    schema = self._translate_schema_from_server(data.schema)
    frame = VertexFrame(self, data.name, schema, data.vertex_key,
                        data.container_id, data.commit_id)
    return frame

  def create_edge_frame(
      self, name : str, schema : list[list], source : Union[str, VertexFrame],
      target : Union[str, VertexFrame], source_key : str, target_key : str,
      frame_labels : Optional[Mapping[str, Sequence[str]]] = None,
      row_label_universe : Optional[Sequence] = None,
      attempts : int = 1) -> EdgeFrame:
    """
    Create a new EdgeFrame in the server.

    An EdgeFrame represents a collection of edges held on the xGT server that
    share the same property names and types.  This function creates a new
    frame of edges on the xGT server and returns an EdgeFrame representing it.

    Each edge conects a source vertex to a target vertex.  The source_key
    parameter gives the schema property that identifies the source vertex of
    each edge.  The target_key parameter gives the schema property that
    identifies the target vertex of each edge.

    The source vertex of each edge in an EdgeFrame must belong to the same
    VertexFrame.  This source VertexFrame is identified by the source parameter.
    The target vertex of each edge in an EdgeFrame must belong to the same
    VertexFrame.  This target VertexFrame is identified by the target parameter.

    Parameters
    ----------
    name : str
      Name of the frame.  Must be a valid frame name.  The namespace is
      optional, and if not given the default namespace will be used.
    schema : list of lists
      The schema defining the property names and types.  Each row in the frame
      will have these properties.  Given as a list of lists associating property
      names with xGT data types.
    source : str or VertexFrame
      The VertexFrame the source vertex of each edge in this frame belongs to.
      Given as a name of a VertexFrame or a VertexFrame object.
    target : str or VertexFrame
      The VertexFrame the target vertex of each edge in this frame belongs to.
      Given as a name of a VertexFrame or a VertexFrame object.
    source_key : str
      The edge property name that identifies the source vertex of an edge.
    target_key : str
      The edge property name that identifies the target vertex of an edge.
    frame_labels : dictionary
      The permissions to apply to the frame.  Given as a dictionary mapping a
      string to a list of strings.  The key represents the permission type.  The
      value represents the labels required for this permission.  Permission
      types are "create", "read", "update", and "delete".  By default, no labels
      are required.
    row_label_universe : Iterable of strs
      All possible labels to be used for rows inside this frame.  A maximum of
      128 labels are supported for rows in each frame.  By default, no row
      labels are required.
    attempts : int
      Number of times to attempt the creation of the EdgeFrame.  The creation
      will be retried if it fails due to transactional conflicts.

    Returns
    -------
    EdgeFrame
      Frame to the collection of edges.

    Raises
    ------
    XgtNameError
      If the name provided is not a correct frame name.
      If the source_key or target_key are not in the schema.  If the source or
      target VertexFrames are not found.
      If a frame with this name already exists in the namespace.
    XgtSecurityError
      If the user does not have required permissions for this action.
    XgtTransactionError
      If a conflict with another transaction occurs.

    Examples
    --------
    >>> import xgt
    >>> conn = xgt.Connection()
    >>> conn.create_vertex_frame(
    ...   name = 'People',
    ...   schema = [['id', xgt.INT],
    ...             ['name', xgt.TEXT]],
    ...   key = 'id')
    >>> conn.create_vertex_frame(
    ...   name = 'Companies',
    ...   schema = [['id', xgt.INT],
    ...             ['size', xgt.TEXT],
    ...             ['name', xgt.TEXT]],
    ...   key = 'id',
    ...   frame_labels = { 'create' : ['label1'],
    ...                    'delete' : ['label1', 'label2'] })
    >>> conn.create_edge_frame(
    ...   name = 'WorksFor',
    ...   schema = [['srcid', xgt.INT],
    ...             ['role', xgt.TEXT],
    ...             ['trgid', xgt.INT]],
    ...   source = 'People',
    ...   target = 'Companies',
    ...   source_key = 'srcid',
    ...   target_key = 'trgid',
    ...   frame_labels = { 'create' : ['label1'],
    ...                    'update' : ['label3'],
    ...                    'delete' : ['label1', 'label2'] })
    """
    name = _validated_frame_name(name)
    schema = _validated_schema(schema)
    source_key = _validated_property_name(source_key)
    target_key = _validated_property_name(target_key)
    num_columns = len(schema)

    source_col = num_columns
    target_col = num_columns
    for col in range(num_columns):
      if schema[col][0] == source_key:
        source_col = col
      if schema[col][0] == target_key:
        target_col = col

    if source_col == num_columns:
      raise XgtNameError(f'The source key "{source_key}" does not match any '
                         'schema property name in this frame.')
    if target_col == num_columns:
      raise XgtNameError(f'The target key "{target_key}" does not match any '
                         'schema property name in this frame.')

    if isinstance(source, VertexFrame):
      source_name = source.name
    else:
      source_name = _validated_frame_name(source)
    if isinstance(target, VertexFrame):
      target_name = target.name
    else:
      target_name = _validated_frame_name(target)

    request = graph_proto.CreateFrameRequest()
    request.type = sch_proto.FrameTypeEnum.Value('EDGE')
    request.name = name
    request.source_vertex = source_name
    request.target_vertex = target_name
    request.source_key = source_col
    request.target_key = target_col

    _generate_proto_schema_from_xgt_schema(request, schema)

    request = self._container_labels_helper(request, frame_labels,
                                            row_label_universe)

    self._process_kwargs(request, {'attempts':attempts})
    response = self._call(request, self._graph_svc.CreateFrame)

    data = response.container[0]
    schema = self._translate_schema_from_server(data.schema)
    frame = EdgeFrame(self, data.name, schema,
                      data.source_vertex, data.target_vertex,
                      data.source_key, data.target_key,
                      data.container_id, data.commit_id)
    return frame

  # Translate a schema from the protobuf to python representation.
  def _translate_schema_from_server(self, server_schema):
    schema = []
    for prop in server_schema.property:
      prop_type = sch_proto.UvalTypeEnum.Name(prop.data_type).lower()
      if prop_type == 'list':
        leaf_type = sch_proto.UvalTypeEnum.Name(prop.leaf_type).lower()

        if (prop.list_depth == 0):
          schema.append([prop.name, prop_type, leaf_type])
        else:
          schema.append([prop.name, prop_type, leaf_type,
                         prop.list_depth + 1])
      else:
        schema.append([prop.name, prop_type])

    return schema

  def _server_schema_col_name_to_position(self, server_schema, key_name):
    for i, schema_property in enumerate(server_schema.property):
      if schema_property.name == key_name:
        return i

    raise XgtError(f"Cannot find frame key column: {key_name}")

  # Insert the data into a frame for different data types.
  # frame must be a TableFrame, VertexFrame, or EdgeFrame object.
  # Optional parameters can be used for CSV files.
  def _insert_data_into_frame(self, frame, data_source,
                              header_mode = HeaderMode.NONE,
                              delimiter = ',',
                              column_mapping = None,
                              row_labels = None,
                              row_label_columns = None,
                              source_vertex_row_labels = None,
                              target_vertex_row_labels = None,
                              suppress_errors = False,
                              on_duplicate_keys = 'error'):
    additional_args = { }
    if isinstance(frame, EdgeFrame):
      additional_args = {
          'source_vertex_row_labels' : source_vertex_row_labels,
          'target_vertex_row_labels' : target_vertex_row_labels }

    def _load_from_pyarrow(pytab):
      path = frame._build_flight_path(
               row_labels, row_label_columns, suppress_errors,
               column_mapping = column_mapping,
               on_duplicate_keys = on_duplicate_keys, **additional_args)
      frame._write_table_to_flight(pytab, path, None, DEFAULT_CHUNK_SIZE)

    load_success = False

    # If a file or list of files is given, load the data.
    if isinstance(data_source, (str, list)):
      # Use the regular load. The file must have a header to infer the schema.
      if isinstance(frame, VertexFrame):
        frame.load(
            data_source, header_mode = header_mode, delimiter = delimiter,
            column_mapping = column_mapping,
            row_labels = row_labels, row_label_columns = row_label_columns,
            suppress_errors = suppress_errors,
            on_duplicate_keys = on_duplicate_keys, **additional_args)
      else:
        frame.load(
            data_source, header_mode = header_mode, delimiter = delimiter,
            column_mapping = column_mapping,
            row_labels = row_labels, row_label_columns = row_label_columns,
            suppress_errors = suppress_errors, **additional_args)
      load_success = True
    elif isinstance(data_source, pyarrow.Table):
      _load_from_pyarrow(data_source)
      load_success = True
    else:
      try:
        import pandas as pd
        if isinstance(data_source, pd.DataFrame):
          _load_from_pyarrow(pyarrow.Table.from_pandas(data_source))
          load_success = True
      except ModuleNotFoundError:
        pass

    if not load_success:
      raise XgtError(f"Cannot insert data source {data_source} into frame.")

  # Infer a schema from a server side file. Optional parameters can be used for
  # CSV files.
  def _get_schema_from_server_file(self, file_name,
                                   header_mode = HeaderMode.NONE,
                                   delimiter = None):
    if file_name.endswith('.gz') or file_name.endswith('.bz'):
      raise XgtError("Cannot automatically infer xGT frame schema from "
                     f"compressed file {file_name}.")

    request = data_proto.InferSchemaRequest()
    request.file_name = file_name

    _convert_header_mode(header_mode, request)
    request.delimiter = 'infer' if delimiter is None else delimiter

    if (len(self.aws_access_key_id) > 0 and
        len(self.aws_secret_access_key) > 0):
      request.authorization = self.aws_access_key_id + ':' + \
                              self.aws_secret_access_key + ':' + \
                              self.aws_session_token

    response = self._call(request, self._data_svc.InferSchema)
    return [self._translate_schema_from_server(response.schema), response.delimiter]

  # Infer a schema from a client side file. Optional parameters can be used for
  # CSV files.
  def _get_schema_from_client_file(self, file_name,
                                   header_mode = HeaderMode.NONE,
                                   delimiter = None):
    class InvalidRowHandler:
      def __init__(self, result):
          self.result = result

      def __call__(self, row):
          return self.result

      def __eq__(self, other):
          return (isinstance(other, InvalidRowHandler) and
                  other.result == self.result)

      def __ne__(self, other):
          return (not isinstance(other, InvalidRowHandler) or
                  other.result != self.result)

    if file_name.endswith('.gz') or file_name.endswith('.bz'):
      raise XgtError("Cannot automatically infer xGT frame schema from "
                     f"compressed file {file_name}.")

    no_header = header_mode == HeaderMode.NONE

    if file_name.endswith('parquet'):
      parquet_metadata = pyarrow.parquet.read_metadata(file_name)
      pyarrow_schema = pyarrow.parquet.read_schema(file_name)
      return _infer_xgt_schema_from_pyarrow_schema(pyarrow_schema), ','
    else:
      if delimiter is None:
        delimiter = self._infer_delimiter_from_data(self._read_first_lines(file_name, 5))

      pyarrow_csv_read_options = pyarrow.csv.ReadOptions(
                                   autogenerate_column_names = no_header)
      # When inferring we skip bad lines and let the load deal with those.
      pyarrow_csv_parse_options = pyarrow.csv.ParseOptions(
          delimiter = delimiter, ignore_empty_lines = True,
          invalid_row_handler = InvalidRowHandler('skip'))

      # Because the user may not expect arrow to be involved in reading the CSV
      # file, we catch and re-raise an XgtIOError if there are errors reading
      # it.
      try:
        pyarrow_csv_stream_reader = pyarrow.csv.open_csv(
            file_name, read_options = pyarrow_csv_read_options,
            parse_options = pyarrow_csv_parse_options)
        pyarrow_chunk = pyarrow_csv_stream_reader.read_next_batch()
      except Exception as e:
        raise XgtIOError(f"Error reading file {file_name}.") from e

      return _infer_xgt_schema_from_pyarrow_schema(pyarrow_chunk.schema), delimiter

  # Infer a schema from a file. Optional parameters can be used for CSV files.
  def _get_schema_from_file(self, file_name, header_mode = HeaderMode.NONE,
                            delimiter = None):
    # If a file is given, load the data.
    client_paths, server_paths, url_paths = _group_paths(file_name, True)
    if len(server_paths) > 0:
      return self._get_schema_from_server_file(server_paths[0],
                                               header_mode, delimiter)
    elif len(client_paths) > 0:
      # If the file name has * or ? etc, try to expand to a concrete file.
      file_name = client_paths[0]
      glob_files = glob.glob(file_name)
      inferred_delimiters = []
      if len(glob_files) > 0:
        base_schema, inferred_delimiter = self._get_schema_from_client_file(glob_files[0],
                                                                            header_mode, delimiter)
        base_is_parquet = file_name.endswith('parquet')

        if inferred_delimiter != None:
          inferred_delimiters.append(inferred_delimiter)

        for i in range(1, len(glob_files)):
          if base_is_parquet != glob_files[i].endswith('parquet'):
            raise XgtTypeError("Expected all files to have the same CSV or "
                               "parquet type: " + glob_files[i])
          schema, inferred_delimiter = self._get_schema_from_client_file(
              glob_files[i], header_mode, delimiter)
          if inferred_delimiter != None:
            inferred_delimiters.append(inferred_delimiter)
          if base_schema != schema:
            raise XgtTypeError("Expected all files to have the same schema: " +
                               glob_files[i])
        return base_schema, inferred_delimiters
      else:
        schema, inferred_delimiter = self._get_schema_from_client_file(file_name, header_mode,
                                                                       delimiter)
        return schema, [inferred_delimiter]
    elif len(url_paths) > 0:
      return self._get_schema_from_server_file(url_paths[0], header_mode,
                                               delimiter)

  # Infer a schema from a data source. Optional parameters can be used when the
  # data source is a CSV file.
  def _infer_schema_from_data(self, data_source, header_mode = HeaderMode.NONE,
                              delimiter = None):
    # Infer the schema from the data.
    if isinstance(data_source, str):
      return self._get_schema_from_file(data_source, header_mode, delimiter)
    elif isinstance(data_source, list):
      base_schema = None
      inferred_delimiters = []
      for file_name in data_source:
        if isinstance(file_name, str):
          schema, inferred_delimiter = self._get_schema_from_file(
            file_name, header_mode, delimiter)
          if len(inferred_delimiter) > 0:
            inferred_delimiters.extend(inferred_delimiter)
          elif delimiter is None:
            inferred_delimiters.append(',')
          if base_schema is None:
            base_schema = schema
          if schema != base_schema:
            raise XgtTypeError("Expected all files to have the same schema: " +
                               file_name)
      if base_schema is None:
        raise XgtError("Cannot automatically infer xGT frame schema from empty "
                       "file name list.")
      return base_schema, inferred_delimiters
    elif isinstance(data_source, pyarrow.Table):
      return _infer_xgt_schema_from_pyarrow_schema(data_source.schema), [',']
    else:
      try:
        import pandas as pd
        if isinstance(data_source, pd.DataFrame):
          as_arrow = pyarrow.Table.from_pandas(data_source)
          return _infer_xgt_schema_from_pyarrow_schema(as_arrow.schema), [',']
      except ModuleNotFoundError:
        pass

    raise XgtError("Cannot automatically infer xGT frame schema from data of "
                   f"type {type(data_source)}.")

  def _read_first_lines(self, filename, line_count):
    lines = ''
    with open(filename, 'r') as file:
      current_line_count = 0
      while current_line_count < line_count:
        line = file.readline()
        if not line:
          break
        lines += line
        current_line_count += 1

    return lines

  def _infer_delimiter_from_data(self, csv_content_sample):
    lines = re.split(r'\r?\n', csv_content_sample)

    # Define possible delimiters
    delimiters = [',', '\t', '|', ':', ' ']

    # Initialize a dictionary to store field counts for each delimiter
    delimiter_field_counts = {delimiter: [] for delimiter in delimiters}

    # Calculate field counts for each line and delimiter
    for line in lines:
      if line == '':
        continue;
      for delimiter in delimiters:
        count = 1  # Start with 1 because there's at least one field
        inside_quotes = False  # Track if we're inside quotes
        quote_type = '"'  # Track the type of quote
        escape_next = False  # Track if the current character is escaped

        for char in line:
          # Handle escape sequences
          if escape_next:
            escape_next = False
            continue

          if char == '\\':
            escape_next = True
            continue

          # Toggle quote state if we encounter a quote and it's not escaped
          if char == '"' or char == "'":
            if not inside_quotes or (inside_quotes and quote_type == char):
              inside_quotes = not inside_quotes
              quote_type = char

          # Only count delimiter if we're not inside quotes
          if not inside_quotes and char == delimiter:
            count += 1

        delimiter_field_counts[delimiter].append(count)

    best_delimiter = delimiters[0]
    lowest_variance = float('inf')
    chosen_field_count = 0

    # Calculate variance for each delimiter and find the one with the lowest variance
    for delimiter, field_counts in delimiter_field_counts.items():
      zero_count = field_counts.count(1)

      # Ignore delimiters where most lines have a field count of 1
      if zero_count < len(lines) / 2:
        mean = sum(field_counts) / len(field_counts) if len(field_counts) > 0 else 0
        variance = statistics.variance(field_counts) if len(field_counts) > 1 else 0

        if variance < lowest_variance or (variance == lowest_variance and mean > chosen_field_count):
          chosen_field_count = mean
          lowest_variance = variance
          best_delimiter = delimiter

    return best_delimiter

  def get_schema_from_data(
      self, data_source : Union[str, Iterable[str], pandas.DataFrame,
                                pyarrow.Table],
      header_mode : str = HeaderMode.NONE,
      delimiter : Optional[str] = None,
      column_mapping : Optional[Mapping[str, Union[str, int]]] = None,
      row_label_columns : Optional[Sequence[str]] = None,
      inferred_delimiters : Sequence[str] = []) -> list[list]:
    """
    Get back an inferred frame schema from the data source passed in.  (Beta)

    Note that this is not the schema of an existing frame, but can be used to
    create a new frame.
    The data schema can contain the following types: string, integer,
    floating point, double, boolean, date, time, and datetime.

    Parameters
    ----------
    data_source : str, list of str, pyarrow Table, pandas DataFrame
      The data source from which to create a frame.  If a string or list of
      strings, each entry must be a file path possibly with wildcards.
      For the file path, the same protocols are supported as load().
      Refer to load().
    header_mode : str
      Indicates how the file header should be processed:
        - HeaderMode.NONE:
          No header exists.
        - HeaderMode.IGNORE:
          Ignore the first line containing the header.
        - HeaderMode.NORMAL:
          Process the header in non-strict mode.  If a schema column is missing,
          a null value is ingested for that schema column.  Any file column
          whose name does not correspond to a schema column or a security label
          column is ignored.
        - HeaderMode.STRICT:
          Process the header in strict mode.  The name of each header column
          should correspond to a schema column, a security label column, or be
          named IGNORE.  Each schema column must appear in the file.

      Only applies to CSV files.
    delimiter : str
      Delimiter for CSV data.
      Only applies to CSV files.
      Can be a character or none which will infer the character.
    column_mapping : dictionary
      Maps the frame column names to input columns for the ingest.  The key of
      each element is frame's column name.  The value is either the name of the
      input column (from the file header, pandas, or arrow table names) or the
      file column index.  If file column names are used, the header_mode must be
      NORMAL.  If only file column indices are used, the header_mode can be
      NORMAL, NONE, or IGNORE.

      .. versionadded:: 1.15.0
    inferred_delimiter : list of str
      If the delimiter passed is None, this field will be populated with the
      delimiters for each file.

      .. versionadded:: 2.0.6

    Raises
    ------
    XgtIOError
      If there are errors in reading the data.
    XgtTypeError
      If the data source contains data types not supported for automatic
      schema inference.

    Returns
    -------
    list of lists
      Describes a schema for an xGT frame, with property names and types.
    """
    schema, result_delimiters = self._infer_schema_from_data(
        data_source, header_mode, delimiter)
    # TODO(josh):
    # This should probably be a map of files to delimiters for wild card cases
    # since the ordering doesn't indicate much.
    # The wild card case isn't too useful ATM until we fully support loading
    # multiple files with different delimiters.
    inferred_delimiters[:] = result_delimiters

    if column_mapping is not None:
      schema = _apply_mapping_to_schema(schema, column_mapping)
    elif row_label_columns is not None:
      schema = _remove_label_columns_from_schema(schema, row_label_columns)
    if header_mode == HeaderMode.STRICT:
      schema = [entry for entry in schema if entry[0] != 'IGNORE']
    return schema

  def create_table_frame_from_data(
      self, data_source : Union[str, Iterable[str], pandas.DataFrame,
                                pyarrow.Table],
      name : str, schema : Optional[list[list]] = None,
      header_mode : str = HeaderMode.NONE, delimiter : Optional[str] = None,
      column_mapping : Optional[Mapping[str, Union[str, int]]] = None,
      frame_labels : Optional[Sequence[str]] = None,
      row_label_universe : Optional[Sequence] = None,
      row_labels : Optional[Sequence[str]] = None,
      row_label_columns : Optional[Sequence[str]] = None,
      suppress_errors : bool = False,
      on_duplicate_keys : str = 'error') -> TableFrame:
    """
    Create a new TableFrame in the server based on the data source.  (Beta)

    The schema of the frame will be automatically inferred from the data passed
    in as data_source and the data will be inserted into the frame.

    Parameters
    ----------
    data_source : str, list of str, pyarrow Table, pandas DataFrame
      The data source from which to create a frame.  If a string or list of
      strings, each entry must be a file path possibly with wildcards.
      For the file path, the same protocols are supported as load().
      Refer to load().
    name : str
      Must be a valid frame name.  The namespace is optional, and if not given
      it will use the default namespace.
    schema : list of lists
      List of lists associating property names with xGT data types.
      Each row in the TableFrame will have these properties.

      Default is None.  If None, the schema is inferred from data_source.
    header_mode : str
      Indicates how the file header should be processed:
        - HeaderMode.NONE:
          No header exists.
        - HeaderMode.IGNORE:
          Ignore the first line containing the header.
        - HeaderMode.NORMAL:
          Process the header in non-strict mode.  If a schema column is missing,
          a null value is ingested for that schema column.  Any file column whose
          name does not correspond to a schema column or a security label column
          is ignored.
        - HeaderMode.STRICT:
          Process the header in strict mode.  The name of each header column
          should correspond to a schema column, a security label column, or be
          named IGNORE.  Each schema column must appear in the file.

      Only applies to CSV files.
    delimiter : str
      Delimiter for CSV data.
      Only applies to CSV files.
      Can be a character or none which will infer the character.
    column_mapping : dictionary
      Maps the frame column names to file columns for the ingest.
      The key of each element is frame's column name.  The value is either the
      name of the file column (from the file header) or the file column index.
      If file column names are used, the header_mode must be NORMAL.  If only
      file column indices are used, the header_mode can be NORMAL, NONE, or
      IGNORE.

      .. versionadded:: 1.15.0
    frame_labels : dictionary
      A dictionary mapping a string to a list of strings.  The key represents
      the permission type.  The value represents the labels required for this
      permission.  Permission types are create, read, update, and delete.
      By default, no labels are required.
    row_label_universe : Iterable of strs
      An iterable of all possible labels to be used for rows inside this edge
      frame.  A maximum of 128 labels are supported for rows in each frame.  By
      default, no row labels are required.
    row_labels : list
      A list of security labels to attach to each row inserted with the load.
      Each label must have been passed in to the row_label_universe
      parameter when creating the frame.  Note: Only one of row_labels
      and row_label_columns must be passed.
    row_label_columns: list
      A list of columns indicating which columns in the CSV file contain
      security labels to attach to the inserted row. If the header mode is
      NONE or IGNORE, this must be a list of integer column indices.  If the
      header mode is NORMAL or STRICT, this must be a list of string column
      names.  Note: Only one of row_labels and
      row_label_columns must be passed.
    suppress_errors : bool
      If true, continues to load data if an ingest error is encountered,
      placing the first 1000 errors into the job history.
      If false, stops on first error and raises.  Defaults to False.

    Raises
    ------
    XgtNameError
      If the name provided is not a correct frame name or
      a frame with this name already exists in the namespace.
    XgtIOError
      If there are errors in the data being inserted or some data could
      not be inserted into the frame.
    XgtTypeError
      If the data source contains data types not supported by this method.
    XgtSecurityError
      If the user does not have required permissions for this action.
    XgtTransactionError
      If a conflict with another transaction occurs.

    Returns
    -------
    TableFrame
      Frame containing the data passed in.
    """
    inferred_delimiters = []
    if schema is None:
      schema = self.get_schema_from_data(data_source, header_mode = header_mode,
          delimiter = delimiter, column_mapping = column_mapping,
          row_label_columns = row_label_columns, inferred_delimiters = inferred_delimiters)

    if delimiter is None and len(inferred_delimiters) > 0:
      first_delim = inferred_delimiters[0]
      for index, delim in enumerate(inferred_delimiters):
        if delim != first_delim:
          name = data_source[index] if len(inferred_delimiters) == len(data_source) else 'Wildcard files different.'
          raise XgtTypeError("Expected all files to have the same delimiter: " +
                             name)
      delimiter = inferred_delimiters[0]
    elif delimiter is None and len(inferred_delimiters) == 0:
      delimiter = ','
    # Create the frame.
    frame = self.create_table_frame(name = name, schema = schema,
                                    frame_labels = frame_labels,
                                    row_label_universe = row_label_universe)

    # Insert the data.
    self._insert_data_into_frame(
        frame, data_source, header_mode = header_mode, delimiter = delimiter,
        column_mapping = column_mapping,
        row_labels = row_labels, row_label_columns = row_label_columns,
        suppress_errors = suppress_errors)

    return frame

  def create_vertex_frame_from_data(
      self, data_source : Union[str, Iterable[str], pandas.DataFrame,
                                pyarrow.Table],
      name : str, key : str , schema : Optional[list[list]] = None,
      header_mode : str = HeaderMode.NONE, delimiter : Optional[str] = None,
      column_mapping : Optional[Mapping[str, Union[str, int]]] = None,
      frame_labels : Optional[Sequence[str]] = None,
      row_label_universe : Optional[Sequence] = None,
      row_labels : Optional[Sequence[str]] = None,
      row_label_columns :  Optional[Sequence[str]] = None,
      suppress_errors : bool = False,
      on_duplicate_keys : str = 'error') -> VertexFrame:
    """
    Create a new VertexFrame in the server based on the data source.  (Beta)

    The schema of the frame will be automatically inferred from the data passed
    in as data_source and the data will be inserted into the frame.

    Parameters
    ----------
    data_source : str, list of str, pyarrow Table, pandas DataFrame
      The data source from which to create a frame.  If a string or list of
      strings, each entry must be a file path possibly with wildcards.
      For the file path, the same protocols are supported as load().
      Refer to load().
    name : str
      Must be a valid frame name.  The namespace is optional, and if not given
      it will use the default namespace.
    key : str
      The property name used to uniquely identify vertices in the graph.
      This is the name of one of the properties from the schema and
      must be unique for each vertex in the frame.
      Note that the schema will be automatically inferred from the data_source
      and may be affected by the header_mode and column_mapping parameters.
    schema : list of lists
      List of lists associating property names with xGT data types.
      Each vertex in the VertexFrame will have these properties.

      Default is None.  If None, the schema is inferred from data_source.
    header_mode : str
      Indicates how the file header should be processed:
        - HeaderMode.NONE:
          No header exists.
        - HeaderMode.IGNORE:
          Ignore the first line containing the header.
        - HeaderMode.NORMAL:
          Process the header in non-strict mode.  If a schema column is missing,
          a null value is ingested for that schema column.  Any file column whose
          name does not correspond to a schema column or a security label column
          is ignored.
        - HeaderMode.STRICT:
          Process the header in strict mode.  The name of each header column
          should correspond to a schema column, a security label column, or be
          named IGNORE.  Each schema column must appear in the file.

      Only applies to CSV files.
    delimiter : str
      Delimiter for CSV data.
      Only applies to CSV files.
      Can be a character or none which will infer the character.
    column_mapping : dictionary
      Maps the frame column names to file columns for the ingest.
      The key of each element is frame's column name.  The value is either the
      name of the file column (from the file header) or the file column index.
      If file column names are used, the header_mode must be NORMAL.  If only
      file column indices are used, the header_mode can be NORMAL, NONE, or
      IGNORE.

      .. versionadded:: 1.15.0
    frame_labels : dictionary
      A dictionary mapping a string to a list of strings.  The key represents
      the permission type.  The value represents the labels required for this
      permission.  Permission types are create, read, update, and delete.
      By default, no labels are required.
    row_label_universe : Iterable of strs
      An iterbale of all possible labels to be used for rows inside this edge
      frame.  A maximum of 128 labels are supported for rows in each frame.  By
      default, no row labels are required.
    row_labels : list
      A list of security labels to attach to each row inserted with the load.
      Each label must have been passed in to the row_label_universe
      parameter when creating the frame.  Note: Only one of row_labels
      and row_label_columns must be passed.
    row_label_columns: list
      A list of columns indicating which columns in the CSV file contain
      security labels to attach to the inserted row.  If the header mode is
      NONE or IGNORE, this must be a list of integer column indices.  If the
      header mode is NORMAL or STRICT, this must be a list of string column
      names.  Note: Only one of row_labels and
      row_label_columns must be passed.
    suppress_errors : bool
      If true, continues to load data if an ingest error is encountered,
      placing the first 1000 errors into the job history.
      If false, stops on first error and raises.  Defaults to False.
    on_duplicate_keys : {‘error’, ‘skip’, 'skip_same'}, default 'error'
      Specifies what to do upon encountering a duplicate key.

      Allowed values are :
        - 'error', raise an Exception when a duplicate key is found.
        - 'skip', skip duplicate keys without raising.
        - 'skip_same', skip duplicate keys if the row is exactly the same
          without raising.

      .. versionadded:: 1.13.0

    Raises
    ------
    XgtNameError
      If the name provided is not a correct frame name or a frame with this
      name already exists in the namespace.  If the key parameter cannot be
      found in the schema of data_source or in the schema parameter.  If
      column_mapping is used, the key should be found there.
    XgtIOError
      If there are errors in the data being inserted or some data could
      not be inserted into the frame.
    XgtTypeError
      If the data source contains data types not supported by this method.
    XgtSecurityError
      If the user does not have required permissions for this action.
    XgtTransactionError
      If a conflict with another transaction occurs.

    Returns
    -------
    VertexFrame
      Frame to the collection of vertices.
    """
    inferred_delimiters = []
    if schema is None:
      schema = self.get_schema_from_data(
          data_source, header_mode = header_mode, delimiter = delimiter,
          column_mapping = column_mapping,
          row_label_columns = row_label_columns, inferred_delimiters = inferred_delimiters)

    if delimiter is None and len(inferred_delimiters) > 0:
      first_delim = inferred_delimiters[0]
      for index, delim in enumerate(inferred_delimiters):
        if delim != first_delim:
          raise XgtTypeError("Expected all files to have the same delimiter: " +
                             data_source[index])
      delimiter = inferred_delimiters[0]
    elif delimiter is None and len(inferred_delimiters) == 0:
      delimiter = ','

    actual_key = _find_key_in_schema(key, schema)

    # Create the frame.
    frame = self.create_vertex_frame(name = name, schema = schema,
                                     key = actual_key,
                                     frame_labels = frame_labels,
                                     row_label_universe = row_label_universe)

    # Insert the data.
    self._insert_data_into_frame(
        frame, data_source, header_mode = header_mode, delimiter = delimiter,
        column_mapping = column_mapping,
        row_labels = row_labels, row_label_columns = row_label_columns,
        suppress_errors = suppress_errors,
        on_duplicate_keys = on_duplicate_keys)

    return frame

  def create_edge_frame_from_data(
      self, data_source : Union[str, Iterable[str], pandas.DataFrame,
                                pyarrow.Table],
      name : str, source : Union[str, VertexFrame],
      target : Union[str, VertexFrame], source_key : str, target_key : str,
      schema : Optional[list[list]] = None,
      header_mode : str = HeaderMode.NONE, delimiter : Optional[str] = None,
      column_mapping : Optional[Mapping[str, Union[str, int]]] = None,
      frame_labels : Optional[Sequence[str]] = None,
      row_label_universe : Optional[Sequence] = None,
      row_labels : Optional[Sequence[str]] = None,
      row_label_columns : Optional[Sequence[str]] = None,
      source_vertex_row_labels : Optional[Sequence[str]] = None,
      target_vertex_row_labels : Optional[Sequence[str]] = None,
      suppress_errors : bool = False,
      on_duplicate_keys : str = 'error') -> EdgeFrame:
    """
    Create a new EdgeFrame in the server based on the data source.  (Beta)

    The schema of the frame will be automatically inferred from the data passed
    in as data_source and the data will be inserted into the frame.

    Parameters
    ----------
    data_source : str, list of str, pyarrow Table, pandas DataFrame
      The data source from which to create a frame.  If a string or list of
      strings, each entry must be a file path possibly with wildcards.
      For the file path, the same protocols are supported as load().
      Refer to load().
    name : str
      Must be a valid frame name.  The namespace is optional, and if not given
      it will use the default namespace.
    source : str
      The name of a VertexFrame.
      The source vertex of each edge in this EdgeFrame will belong
      to this VertexFrame.  This frame will be automatically created if it
      does not already exist.
    target : str
      The name of a VertexFrame.
      The target vertex of each edge in this EdgeFrame will belong
      to this VertexFrame.  This frame will be automatically created if it
      does not already exist.
    source_key : str
      The edge property name that identifies the source vertex of an edge.
      This is one of the properties from the schema.
      Note that the schema will be automatically inferred from the data_source
      and may be affected by the header_mode and column_mapping parameters.
    target_key : str
      The edge property name that identifies the target vertex of an edge.
      This is one of the properties from the schema.
      Note that the schema will be automatically inferred from the data_source
      and may be affected by the header_mode and column_mapping parameters.
    schema : list of lists
      List of lists associating property names with xGT data types.
      Each edge in the EdgeFrame will have these properties.

      Default is None.  If None, the schema is inferred from data_source.
    header_mode : str
      Indicates how the file header should be processed:
        - HeaderMode.NONE:
          No header exists.
        - HeaderMode.IGNORE:
          Ignore the first line containing the header.
        - HeaderMode.NORMAL:
          Process the header in non-strict mode.  If a schema column is missing,
          a null value is ingested for that schema column.  Any file column
          whose name does not correspond to a schema column or a security label
          column is ignored.
        - HeaderMode.STRICT:
          Process the header in strict mode.  The name of each header column
          should correspond to a schema column, a security label column, or be
          named IGNORE.  Each schema column must appear in the file.

      Only applies to CSV files.
    delimiter : str
      Delimiter for CSV data.
      Only applies to CSV files.
      Can be a character or none which will infer the character.
    column_mapping : dictionary
      Maps the frame column names to file columns for the ingest.
      The key of each element is frame's column name.  The value is either the
      name of the file column (from the file header) or the file column index.
      If file column names are used, the header_mode must be NORMAL.  If only
      file column indices are used, the header_mode can be NORMAL, NONE, or
      IGNORE.

      .. versionadded:: 1.15.0
    frame_labels : dictionary
      A dictionary mapping a string to a list of strings.  The key represents
      the permission type.  The value represents the labels required for this
      permission.  Permission types are create, read, update, and delete.
      By default, no labels are required.
    row_label_universe : Iterable of strs
      An iterable of all possible labels to be used for rows inside this edge
      frame.  A maximum of 128 labels are supported for rows in each frame.  By
      default, no row labels are required.
    row_labels : list
      A list of security labels to attach to each row inserted with the load.
      Each label must have been passed in to the row_label_universe
      parameter when creating the frame.  Note: Only one of row_labels
      and row_label_columns must be passed.
    row_label_columns: list
      A list of columns indicating which columns in the CSV file contain
      security labels to attach to the inserted row.  If the header mode is
      NONE or IGNORE, this must be a list of integer column indices.  If the
      header mode is NORMAL or STRICT, this must be a list of string column
      names.  Note: Only one of row_labels and
      row_label_columns must be passed.
    source_vertex_row_labels : list
      A list of security labels to attach to each source vertex that is
      implicitly inserted.  Each label must have been passed in to the
      row_label_universe parameter when creating the frame.
    target_vertex_row_labels : list
      A list of security labels to attach to each target vertex that is
      implicitly inserted.  Each label must have been passed in to the
      row_label_universe parameter when creating the frame.
    suppress_errors : bool
      If true, continues to load data if an ingest error is encountered,
      placing the first 1000 errors into the job history.
      If false, stops on first error and raises.  Defaults to False.

    Raises
    ------
    XgtNameError
      If the name provided is not a correct frame name or
      a frame with this name already exists in the namespace.
      If the source_key or target_key parameters cannot be found in the schema
      of data_source or in the schema parameter.
      If column_mapping is used, the keys should be found there.
    XgtIOError
      If there are errors in the data being inserted or some data could
      not be inserted into the frame.
    XgtTypeError
      If the data source contains data types not supported by this method.
      If the source or target vertex frames exist with an incompatible
      key type.
    XgtSecurityError
      If the user does not have required permissions for this action.
    XgtTransactionError
      If a conflict with another transaction occurs.

    Returns
    -------
    EdgeFrame
      Frame to the collection of edges.
    """
    inferred_delimiters = []
    if schema is None:
      schema = self.get_schema_from_data(
          data_source, header_mode = header_mode, delimiter = delimiter,
          column_mapping = column_mapping,
          row_label_columns = row_label_columns)

    if delimiter is None and len(inferred_delimiters) > 0:
      first_delim = inferred_delimiters[0]
      for index, delim in enumerate(inferred_delimiters):
        if delim != first_delim:
          raise XgtTypeError("Expected all files to have the same delimiter: " +
                             data_source[index])
      delimiter = inferred_delimiters[0]
    elif delimiter is None and len(inferred_delimiters) == 0:
      delimiter = ','
    actual_source_key = _find_key_in_schema(source_key, schema)
    actual_target_key = _find_key_in_schema(target_key, schema)

    # Create the source and target vertex frames if needed.

    def _check_and_create_endpoint_vertex_frame(vertex_frame_name,
                                                vertex_key, schema):
      existing_vertex_frames = [f.name for f in
                                self.get_frames(frame_type = 'vertex')]
      key_type = None
      if vertex_frame_name not in existing_vertex_frames:
        for prop in schema:
          if prop[0] == vertex_key:
            # This assumes that lists are NOT allowed as keys.
            key_type = prop[1]
            break

        if key_type is None:
          raise XgtError('Cannot find the requested endpoint vertex frame '
                         f'key {vertex_key} in the schema of the data.')

        self.create_vertex_frame(name = vertex_frame_name,
                                 schema = [['id', key_type]], key = 'id',
                                 frame_labels = frame_labels,
                                 row_label_universe = row_label_universe)

    _check_and_create_endpoint_vertex_frame(source, actual_source_key, schema)
    _check_and_create_endpoint_vertex_frame(target, actual_target_key, schema)

    frame = self.create_edge_frame(name = name, schema = schema,
                                   source = source,
                                   target = target,
                                   source_key = actual_source_key,
                                   target_key = actual_target_key,
                                   frame_labels = frame_labels,
                                   row_label_universe = row_label_universe)

    # Insert the data.
    self._insert_data_into_frame(
        frame, data_source, header_mode, delimiter = delimiter,
        column_mapping = column_mapping,
        row_labels = row_labels, row_label_columns = row_label_columns,
        source_vertex_row_labels = source_vertex_row_labels,
        target_vertex_row_labels = target_vertex_row_labels,
        suppress_errors = suppress_errors)

    return frame

  def drop_namespace(self, namespace : str, force_drop : bool = False,
                     attempts : int = 10) -> bool:
    """
    Drop a namespace from the server.

    Parameters
    ----------
    name : str
      The name of the namespace to drop.
    force_drop : bool
      If True, the namespace will be dropped even if it is not empty along with
      any frames it contains.  If False, a non-empty namespace will not be
      dropped.
    attempts : int
      Number of times to attempt the deletion of the namespace.
      It will be retried if it fails due to transactional conflicts.

    Returns
    -------
    bool
      True if the namespace was found and dropped.  False if the namespace was
      not found.

    Raises
    ------
    XgtFrameDependencyError
      If the namespace is not empty and force_drop is False.
    XgtNameError
      If the name provided does not follow rules for namespace names.
      A namespace name cannot contain "__", which is used as a separator
      between namespace and name in frame names.
    XgtSecurityError
      If the user does not have required permissions for this action.
    XgtTransactionError
      If a conflict with another transaction occurs.

    Examples
    --------
    >>> import xgt
    >>> conn = xgt.Connection()
    >>> labels = { 'create' : ['label1', 'label2'],
    ...            'read'   : ['label1'],
    ...            'update' : ['label1'],
    ...            'delete' : ['label1', 'label2', 'label3'] }
    >>> conn.create_namespace('career', labels)
    >>> conn.drop_namespace('career')
    >>> conn.drop_namespace('career', force_drop = True)
    """
    request = graph_proto.DeleteNamespaceRequest()
    request.name = namespace
    request.force_drop = force_drop
    self._process_kwargs(request, {'attempts':attempts})
    response = self._call(request, self._graph_svc.DeleteNamespace)
    return response.found_and_deleted

  def drop_graph(self, graph : Union[str, GraphFrame],
                 attempts : int = 10) -> bool:
    """
    Drop a graph frame from the server.

    Parameters
    ----------
    graph : str | GraphFrame
      The name or frame instance of the graph to drop.
    attempts : int
      Number of times to attempt the deletion of the graph.
      It will be retried if it fails due to transactional conflicts.

    Returns
    -------
    bool
      True if the graph was found and dropped.  False if the graph was
      not found.

    Raises
    ------
    XgtNameError
      If the name provided does not follow rules for frame names.
    XgtTypeError
      If the graph parameter is not a string or GraphFrame
    XgtSecurityError
      If the user does not have required permissions for this action.
    XgtTransactionError
      If a conflict with another transaction occurs.
    XgtTypeError
      If the given frame is not a str or GraphFrame.

    Examples
    --------
    >>> import xgt
    >>> conn = xgt.Connection()
    >>> labels = { 'create' : ['label1', 'label2'],
    ...            'read'   : ['label1'],
    ...            'update' : ['label1'],
    ...            'delete' : ['label1', 'label2', 'label3'] }
    >>> conn.create_graph('graph',
                          { 'v0' : 'Vertex0', 'v1' : 'other__Vertex0',
                            'edge' : 'Edge' }, labels)
    >>> conn.drop_graph('graph')

    .. experimental:: The API of this method may change in future releases.
    """
    request = graph_proto.DeleteGraphRequest()
    if isinstance(graph, str):
      request.name = graph
    elif isinstance(graph, GraphFrame):
      request.name = graph.name
    else:
      raise XgtTypeError("Expected a string or GraphFrame for drop_graph()")
    self._process_kwargs(request, {'attempts':attempts})
    response = self._call(request, self._graph_svc.DeleteGraph)
    return response.found_and_deleted

  def drop_frame(self, frame : Union[str, VertexFrame, EdgeFrame, TableFrame],
                 attempts : int = 10) -> bool:
    """
    Drop a VertexFrame, EdgeFrame, or TableFrame.

    Parameters
    ----------
    frame : str, VertexFrame, EdgeFrame, or TableFrame
      A frame or the name of a frame to drop on the xGT server.  The namespace
      is optional for a frame name, and if not given it will use the default
      namespace.
    attempts : int
      Number of times to attempt the deletion of the frame.
      It will be retried if it fails due to transactional conflicts.

    Returns
    -------
    bool
      True if frame was found and dropped and False if frame was not found.

    Raises
    ------
    XgtFrameDependencyError
      If another frame depends on this frame.  The dependent frame should be
      dropped first.
    XgtSecurityError
      If the user does not have required permissions for this action.
    XgtTransactionError
      If a conflict with another transaction occurs.
    XgtTypeError
      If the given frame is not a str, TableFrame, VertexFrame, or EdgeFrame.
    """
    if not isinstance(frame, (str, TableFrame)):
      raise TypeError('Invalid argument: "frame" must be a string or frame')

    return self.drop_frames([frame], attempts)

  def drop_frames(self, frames : Iterable[str], attempts : int = 10) -> bool:
    """
    Drop a VertexFrame, EdgeFrame, or TableFrame.

    .. versionadded:: 1.14.0

    Parameters
    ----------
    frames : list of str, VertexFrame, EdgeFrame, or TableFrame
      A potentially mixed list of frames or names of frames to drop on the xGT
      server.  The namespace is optional for frame names, and if not given it
      will use the default namespace.
    attempts : int
      Number of times to attempt the deletion of the frames.
      It will be retried if it fails due to transactional conflicts.

    Returns
    -------
    bool
      True if frame was found and dropped and False if frame was not found.

    Raises
    ------
    XgtFrameDependencyError
      If another frame depends on this frame.  The dependent frame should be
      dropped first.
    XgtSecurityError
      If the user does not have required permissions for this action.
    XgtTransactionError
      If a conflict with another transaction occurs.
    XgtTypeError
      If a given frame is not a str, TableFrame, VertexFrame, or EdgeFrame.
    """
    if frames is None or not isinstance(frames, Iterable):
      raise TypeError('Invalid argument: "frames" must be a list of '
                      'strings or frames')
    if len(frames) == 0:
      return

    validated_names = []
    for frame in frames:
      if isinstance(frame, TableFrame):
        validated_names.append(frame.name)
      else:
        if not isinstance(frame, str):
          raise TypeError('Invalid argument: "frames" must be a list of '
                          'strings or frames')
        validated_names.append(frame)

    request = graph_proto.DeleteFramesRequest()
    request.name.extend(validated_names)
    self._process_kwargs(request, {'attempts':attempts})
    response = self._call(request, self._graph_svc.DeleteFrames)
    return response.found_and_deleted

  def get_frame_labels(self, frame : str) -> Mapping[str, Sequence[str]]:
    """
    Retrieve the current security labels (CRUD) on a specific frame.

    Parameters
    ----------
    frame : str, VertexFrame, EdgeFrame, or TableFrame
      A frame or the name of a frame from which to retrieve the security labels.

    Returns
    -------
    dict
      A dictionary in the form:

      .. code-block:: python

        {
          "create" : ['label1', ... ],
          "read" : ['label1', ... ],
          "update" : ['label1', ... ],
          "delete" : ['label1', ... ],
        }

    Raises
    ------
    XgtNameError
      If the name provided is not a correct frame name.
    XgtSecurityError
      If the user does not have required permissions for this action.
    XgtTransactionError
      If a conflict with another transaction occurs.
    """
    if isinstance(frame, TableFrame):
      name = frame.name
    else:
      name = _validated_frame_name(frame)
    request = graph_proto.GetFrameLabelsRequest()
    request.name = name
    response = self._call(request, self._graph_svc.GetFrameLabels)
    try:
      access_labels = response.frame_label_map.access_labels
    except:
      return response
    label_map = dict()
    for key in access_labels.keys():
      label_map[key] = [_ for _ in access_labels[key].label]
    return label_map

  def get_user_labels(self) -> Sequence[str]:
    """
    Retrieve the current security labels of the user.

    Returns
    -------
    list of str
      A list of strings corresponding to the security labels of the user.
    """
    request = graph_proto.GetUserLabelsRequest()
    response = self._call(request, self._graph_svc.GetUserLabels)
    return response.user_labels.label

  #------------------------- Job Methods

  def get_jobs(self, jobids : Optional[Sequence[int]] = None) -> list[Job]:
    """
    Get a list of Job objects, each representing the state of
    the job on the server at the point in time of the
    invocation of this function.

    Parameters
    ----------
    jobids : list of ints
      A list of job IDs for which to return Job objects.
      By default, all jobs are returned.

    Returns
    -------
    list
      A list of Job objects, each representing the state
      of a job in the server.

    Examples
    --------
    >>> conn = xgt.Connection()
    >>> ... create vertices and edges and run queries ...
    >>> all_jobs = conn.get_jobs()
    >>> for j in all_jobs:
    >>> ... print j
    id:6, status:completed
    id:7, status:completed
    id:8, status:running
    """
    jobs = []
    request = job_proto.GetJobsRequest()
    if (jobids is not None):
      for jobid in jobids:
        request.job_id.extend([jobid])
    responses = self._call(request, self._job_svc.GetJobs)
    for response in responses:
      _assert_noerrors(response)
      if (response.HasField("job_status")):
        jobs.append(response.job_status)
    return [Job(self, i) for i in jobs]

  def cancel_job(self, job : Union[Job, int]) -> bool:
    """
    Cancel the execution of a job in the server.

    A job can be canceled only if it is *running* and will have a status of
    *canceled* after its cancellation.  A job that already had a status of
    *completed* or *failed* before invoking this function will keep that
    status after invoking this function.

    Parameters
    ----------
    job : Job, int
      A Job object or an integer job id to cancel.

    Returns
    -------
    bool
      True if the job was cancelled.  False if the job already had a
      status of completed or failed before invoking this function.

    Raises
    ------
    XgtSecurityError
      If the user does not have required permissions for this action.

    Examples
    --------
    >>> conn = xgt.Connection()
    >>> ... create vertices and edges and run queries ...
    >>> print(conn.cancel_job(18))
    True
    >>> all_jobs = conn.get_jobs()
    >>> for j in all_jobs:
    >>> ... conn.cancel_job(j)
    """
    if isinstance(job, Job):
      jobid = job.id
    elif isinstance(job, int):
      jobid = job
    else:
      raise TypeError("Job must be a Job object or an int.")

    # Get job status.
    request = job_proto.GetJobsRequest()
    request.job_id.extend([jobid])
    responses = self._call(request, self._job_svc.GetJobs)
    # Cancel job if it's not in a terminal state.
    for response in responses: # Expect only one response.
      if (response.HasField("job_status")):
        job_status = response.job_status
        if job_status.status in [sch_proto.JobStatusEnum.Value('SCHEDULED'),
                                 sch_proto.JobStatusEnum.Value('RUNNING')]:
          request = job_proto.CancelJobsRequest()
          request.job_id.extend([jobid])
          self._call(request, self._job_svc.CancelJobs)
          return True
    return False

  def run_job(self, query : str, parameters : Optional[Mapping] = None,
              optlevel : int = 4, description : Optional[str] = None,
              timeout : int = 0, record_history : bool = True,
              use_gql : bool = False):
    """
    Run an OpenCypher or GQL query as a job.  This function blocks
    until the job stops running.

    Parameters
    ----------
    query : str
      One OpenCypher or GQL query string.
    parameters: dict
      Dictionary containing Cypher or GQL parameters.
    optlevel : int
      Sets the level of query optimization.  The valid values are:

        - 0: No optimization.
        - 1: General optimization.
        - 2: WHERE-clause optimization.
        - 3: Degree-cycle optimization.
        - 4: Query order optimization.
    description : str
      Description of the job.
      If description is None, this will default to the query text.
    timeout : int
      Maximum number of seconds that the query should take before being
      automatically canceled.
      A value less than or equal to zero means no limit on the query time.
    record_history : bool
      If true, records the history of the job.
    use_gql : bool
      If true, the query is interpreted using the Graph Query Language (GQL)
      standard.  The default is to interpret the query as OpenCypher.

      .. experimental:: This feature is experimental.

    Returns
    -------
    Job
      A Job object for the query.

    Raises
    ------
    XgtSyntaxError
      If there is a syntax error in the query.
    XgtNameError
      If there is a name error in the query, such as specifying a frame that
      does not exist.
    XgtTypeError
      If there is a type error in the query, such as comparing a schema
      property to the wrong data type.
    XgtValueError
      If there is a value error in the query.
    XgtSecurityError
      If the user does not have required permissions for this action.
    XgtTransactionError
      If a conflict with another transaction occurs.

    Examples
    --------
    >>> conn = xgt.Connection()
    >>> ... create vertices and edges ...
    >>> job = conn.run_job('MATCH (a:Employees) RETURN a.person_id INTO Results1', timeout=200)
    >>> print(job)
    id:20, status:completed

    >>> conn.run_job('MATCH (a) RETURN a.id INTO Results1')
    ...
    xgt.common.XgtValueError: Invalid column name: 'id'
    """
    job_obj = self._launch_job(query, wait=True, optlevel=optlevel,
                               description=description,
                               timeout=timeout, record_history=record_history,
                               parameters=parameters, use_gql=use_gql)
    if job_obj.status == 'failed' or job_obj.status == 'rollback':
      msg = f'Failed job. id={job_obj.id} msg="{job_obj.error}"'
      raise job_obj.error_type(msg, job_obj.trace)
    return job_obj

  def schedule_job(self, query : str, parameters : Optional[Mapping] = None,
                   optlevel : int = 4, description : Optional[str] = None,
                   record_history : bool = True, use_gql : bool = False) -> Job:
    """
    Schedule an OpenCypher or GQL query as a job.  This function returns
    immediately after scheduling the job.

    Parameters
    ----------
    query : str
      One OpenCypher or GQL query string.
    parameters: dict
      Dictionary containing Cypher or GQL parameters.
    optlevel : int
      Sets the level of query optimization.  The valid values are:

        - 0: No optimization.
        - 1: General optimization.
        - 2: WHERE-clause optimization.
        - 3: Degree-cycle optimization.
        - 4: Query order optimization.
    description : str
      Description of the job.
      If description is None, this will default to the query text.
    record_history : bool
      If true, records the history of the job.
    use_gql : bool
      If true, the query is interpreted using the Graph Query Language (GQL)
      standard.  The default is to interpret the query as OpenCypher.

      .. experimental:: This feature is experimental.

    Returns
    -------
    Job
      A Job object representing the job that has been scheduled.

    Raises
    ------
    XgtSyntaxError
      If there is a syntax error in the OpenCypher query.
    XgtNameError
      If there is a name error in the OpenCypher query, such as specifying a frame that
      does not exist.
    XgtTypeError
      If there is a type error in the OpenCypher query, such as comparing a schema
      property to the wrong data type.
    XgtValueError
      If there is a value error in the OpenCypher query.
    XgtSecurityError
      If the user does not have required permissions for this action.

    Examples
    --------
    >>> conn = xgt.Connection()
    >>> ... create vertices and edges ...
    >>> query = 'MATCH (a:Employees) RETURN a.person_id INTO Results1'
    >>> job = conn.schedule_job(query)
    >>> print(job)
    id:25, status:scheduled
    """
    return self._launch_job(query, wait=False, optlevel=optlevel,
                            description=description,
                            timeout=0, record_history=record_history,
                            parameters=parameters, use_gql=use_gql)

  def wait_for_job(self, job : Union[Job, int], timeout : float = 0) -> Job:
    """
    Wait for a job.  This function blocks until the job stops running.

    Parameters
    ----------
    job : Job, int
      A Job object or an integer job id.
    timeout : int
      Number of seconds each job is allowed to execute before being
      automatically cancelled.
      A value less than or equal to zero means no limit on the wait time.

    Returns
    -------
    Job
      A Job object representing the state of the job on the server.

    Raises
    ------
    XgtSecurityError
      If the user does not have required permissions for this action.
    XgtTransactionError
      If a conflict with another transaction occurs.
    XgtError
      If one or more query jobs failed.

    Examples
    --------
    >>> conn = xgt.Connection()
    >>> ... create vertices and edges ...
    >>> qr1 = 'MATCH (a:Employees) RETURN a.person_id INTO Results0'
    >>> jb1 = conn.schedule_job(qr1)
    >>> qr2 = 'MATCH (b:Companies) RETURN b.company_id INTO Results1'
    >>> jb2 = conn.schedule_job(qr2)
    >>> jb1 = conn.wait_for_job(jb1)
    >>> print(jb1)
    id:31, status:completed
    >>> jb2 = conn.wait_for_job(jb2)
    >>> print(jb2)
    id:32, status:completed
    """
    if isinstance(job, Job):
      jobid = job.id
    elif isinstance(job, int):
      jobid = job
    else:
      raise TypeError('Job must be a Job object or an int.')
    if not (timeout is None or isinstance(timeout, numbers.Number)):
      raise TypeError('Timeout must be a number or None.')

    request = job_proto.WaitJobsRequest()
    request.job_id.extend([jobid])
    if (timeout is None):
      request.timeout = 0
    else:
      request.timeout = timeout
    response = self._call(request, self._job_svc.WaitJobs)
    one_job = response.job_status[0]
    job_obj = Job(self, one_job)
    if job_obj.status == 'failed' or job_obj.status == 'rollback':
      msg = f'Failed job. id={jobid} msg="{job_obj.error}"'
      raise job_obj.error_type(msg, job_obj.trace)
    return job_obj

  def get_metrics_status(self) -> str:
    """
    Check whether the metrics cache is on and finished with updates.  A status
    of metrics_complete is only valid for as long as no vertex or edge frames
    are modified or created.

    Returns
    -------
    str
      The status of metrics collection: metrics_completed, metrics_running, or
      metrics_off.

    Examples
    --------
    >>> conn = xgt.Connection()
    >>> conn.get_metrics_status()
    """

    request = metrics_proto.MetricsStatusRequest()
    response = self._call(request, self._metrics_svc.GetMetricsStatus)
    status = metrics_proto.MetricsStatusEnum.Name(response.status).lower()
    return status

  def wait_for_metrics(self, timeout : float = 0) -> bool:
    """
    Wait until the metrics cache is finished with updates.  This function blocks
    until there are no more metrics to update or until metrics collection is
    turned off through the config or until the optional timeout is reached.

    Parameters
    ----------
    timeout : float
      Max number of seconds the function will block.
      A value less than or equal to zero means no limit on the block time.

    Returns
    -------
    bool
      Returns True if metrics collection was finished when the function
      returned.
      Returns False if metrics collection is not finished (if either metrics
      collection didn't complete before the timeout or if metrics cache is off.)

    Examples
    --------
    >>> conn = xgt.Connection()
    >>> finished = conn.wait_for_metrics()
    """

    timeout_time = datetime.now() + timedelta(seconds=timeout)
    check_interval_sec = 0.1
    status = self.get_metrics_status()
    while ((status == 'metrics_running') and
           (timeout is None or timeout <= 0 or datetime.now() < timeout_time)):
      time.sleep(check_interval_sec)
      status = self.get_metrics_status()

    return (status == 'metrics_completed')

  def get_config(self, keys : Optional[Sequence[str]] = None) -> Mapping :
    """
    Get one or more configuration values from the server.
    These values may not be the same as those set by the user.

    Parameters
    ----------
    keys : list of str or None
      If a list, the list of config keys to retrieve.
      If None, all config values are returned.

    Returns
    -------
    dict
      Dictionary of key-value pairs representing configuration information
      from the server.

    Raises
    ------
    XgtNameError
      If any keys requested are not valid.
    XgtSecurityError
      If the user does not have required permissions for this action.
    XgtTransactionError
      If a conflict with another transaction occurs.

    Examples
    --------
    >>> conn = xgt.Connection()
    >>> conf1 = conn.get_config()
    >>> conf2 = conn.get_config(["key1", "key2", ... ])
    """

    if keys is None:
      keys = []
    elif isinstance(keys, str):
      raise TypeError('Invalid get_config argument: "keys" must be a list '
                      'of strings')
    else:
      keys = [str(k) for k in keys]

    request = admin_proto.GetConfigRequest()
    request.key.extend(keys)
    response = self._call(request, self._admin_svc.GetConfig)
    keyvalues = dict()
    for key in response.entries:
      value = response.entries[key]
      if value.HasField("bool_value"):
        keyvalues[key] = value.bool_value
      elif value.HasField("int_value"):
        keyvalues[key] = value.int_value
      elif value.HasField("float_value"):
        keyvalues[key] = value.float_value
      elif value.HasField("string_value"):
        keyvalues[key] = value.string_value
      elif value.HasField("string_array_value"):
        keyvalues[key] = [i for i in value.string_array_value.string_value]
      else:
        raise XgtTypeError(f'Config value for key {key} has an unknown type')
    return keyvalues

  def set_config(self, config_dict : Mapping) -> None:
    """
    Set key-value pairs in the server configuration.

    Parameters
    ----------
    config_dict: dict
      Dictionary containing config key-values.

    Raises
    ------
    XgtNameError
      If any keys provided are not valid.
    XgtTypeError
      If any config values provided are of the wrong type.
    XgtSecurityError
      If the user does not have required permissions for this action.
    XgtTransactionError
      If a conflict with another transaction occurs.

    Examples
    --------
    >>> conn = xgt.Connection()
    >>> conn.set_config({"mykey" : 14, "another_key" : "This string"})
    """

    request = admin_proto.SetConfigRequest()
    for k,v in config_dict.items():
      if isinstance(v, bool):
        request.entries[k].bool_value = v
      elif isinstance(v, int):
        request.entries[k].int_value = v
      elif isinstance(v, float):
        request.entries[k].float_value = v
      elif isinstance(v, str):
        request.entries[k].string_value = v
      else:
        raise XgtTypeError(f'Setting config value for key [{k}] has a value '
                           f'[{v}] whose type is not supported')
    response = self._call(request, self._admin_svc.SetConfig)
    return None

  def set_default_namespace(
        self, default_namespace : Optional[str] = None) -> None:
    """
    Set the default namespace for this user session.

    Parameters
    ----------
    default_namespace: str
      String value to be the default namespace.
      If set to None, this will disable the default namespace.

    Raises
    ------
    XgtNameError
      If the provided string is not valid.
    XgtSecurityError
      If the user does not have required permissions for this action.

    Examples
    --------
    >>> conn = xgt.Connection()
    >>> conn.set_default_namespace("mynamespace")
    """

    namespaces = self.get_namespaces()

    # Handle special case coming from connection init where
    # the namespace defaults to either userid or default
    if isinstance(default_namespace, _DefaultNamespace):
      default_namespace = self._userid if self._userid in namespaces else ''

    if (default_namespace is None):
      default_namespace = ''

    request = admin_proto.SetDefaultNamespaceRequest()
    request.default_namespace = default_namespace
    response = self._call(request, self._admin_svc.SetDefaultNamespace)

    if (default_namespace != '' and default_namespace not in namespaces):
      raise XgtNameError(f"Namespace not found: {default_namespace}.  "
                         "It either does not exist or the user lacks "
                         "permissions to access it.")

    self._default_namespace = default_namespace
    return None

  def get_default_namespace(self) -> str:
    """
    Get the name of the default namespace.

    Returns
    -------
    str
      String value of the default namespace.

    Examples
    --------
    >>> conn = xgt.Connection()
    >>> defaultNamespace = conn.get_default_namespace()
    """

    if self._default_namespace is None:
      request = admin_proto.GetDefaultNamespaceRequest()
      response = self._call(request, self._admin_svc.GetDefaultNamespace)
      self._default_namespace = response.default_namespace

    return self._default_namespace

  def set_default_graph(
        self, default_graph : Optional[Union[str, GraphFrame]] = None) -> None:
    """
    Set the default graph for this user session.

    Parameters
    ----------
    default_graph: str | GraphFrame | None
      Frame name or instance of the default graph for this session.
      If set to None, this will disable the default graph.

    Raises
    ------
    XgtNameError
      If the provided graph name is not valid.
    XgtTypeError
      If the provided parameter is not a string or a GraphFrame
    XgtSecurityError
      If the user does not have required permissions for this action.

    Examples
    --------
    >>> conn = xgt.Connection()
    >>> conn.set_default_graph("mygraph")

    .. experimental:: The API of this method may change in future releases.
    """

    graphs = [ frame.name for frame in self.get_frames(frame_type = 'graph') ]

    if default_graph is None:
      default_graph = ''

    if isinstance(default_graph, str):
      name_actual = default_graph
    elif isinstance(default_graph, GraphFrame):
      name_actual = default_graph.name
    else:
      raise XgtTypeError('The default graph must be a string or GraphFrame instance')

    if _is_qualified_name(name_actual):
      nspace, frame = _parse_qualified_name(name_actual)
      if nspace == self.get_default_namespace():
        name_actual = frame

    if name_actual != '' and name_actual not in graphs:
      raise XgtNameError(f"Graph not found: {name_actual}.  "
                         "It either does not exist or the user lacks "
                         "permissions to access it.")

    request = admin_proto.SetDefaultGraphRequest()
    request.default_graph = name_actual
    response = self._call(request, self._admin_svc.SetDefaultGraph)

    if name_actual != '':
      if _is_qualified_name(name_actual):
        self._default_graph = name_actual
      else:
        self._default_graph = self.get_default_namespace() + FRAME_SEPARATOR + name_actual
    else:
      self._default_graph = None

  def get_default_graph(self) -> GraphFrame:
    """
    Get the frame for the default graph.

    Returns
    -------
    GraphFrame
      Frame of the default graph.

    Examples
    --------
    >>> conn = xgt.Connection()
    >>> defaultGraph = conn.get_default_graph()

    .. experimental:: The API of this method may change in future releases.
    """

    if self._default_graph is None:
      request = admin_proto.GetDefaultGraphRequest()
      response = self._call(request, self._admin_svc.GetDefaultGraph)
      if response.default_graph != '':
        self._default_graph = response.default_graph

    if self._default_graph is not None:
      return self.get_frame(self._default_graph)

    return None

  def _transfer_frame(self, frame_name, userid, password = '',
                      remote_host = 'localhost', port = 8815, do_ssl = False,
                      chain_cert_file = None, client_key_file = None,
                      client_cert_file = None, ssl_server_cn = None):
    request = data_proto.TransferFrameArrowClientRequest()
    request.host = remote_host
    request.port = port
    request.repository_name = frame_name
    request.ssl.do_ssl = do_ssl
    if do_ssl:
      if chain_cert_file is None:
        raise ValueError("To connect with SSL/TLS, chain_cert_file must be "
                         "passed in.")
      if client_key_file is None:
        raise ValueError("To connect with SSL/TLS, client_key_file must be "
                         "passed in.")
      if client_cert_file is None:
        raise ValueError("To connect with SSL/TLS, client_cert_file must be "
                         "passed in.")
      if ssl_server_cn is None:
        raise ValueError("To connect with SSL/TLS, ssl_server_cn must be "
                         "passed in.")

      request.ssl.chain_cert = open(chain_cert_file, 'rb').read()
      request.ssl.client_key = open(client_key_file, 'rb').read()
      request.ssl.client_cert = open(client_cert_file, 'rb').read()
      request.ssl.ssl_server_cn = ssl_server_cn
    request.user_auth.user_name = userid
    request.user_auth.password = password
    response = self._call(request, self._data_svc.TransferFrameArrowClient)

  def _create_csv_packet (self, frames, paths, header_mode, delimiter,
                          suppress_errors, on_duplicate_keys, column_mappings):
    request = data_proto.UploadCSVMultiDataRequest()
    for frame in frames:
      request.frame_name.append(frame.encode('utf-8'))
    for path in paths:
      request.stream_length.append(os.path.getsize(path))
    request.content_type = data_proto.CSV
    request.is_python_insert = False
    request.suppress_errors = suppress_errors
    request.on_duplicate_keys = on_duplicate_keys

    request.delimiter = delimiter

    _convert_header_mode(header_mode, request)
    request.implicit_vertices = True

    if column_mappings is not None:
      for frame, mapping in column_mappings.items():
        _validate_column_mapping_in_ingest(mapping)
        request.column_mappings[frame].CopyFrom(
          _set_column_mapping_in_ingest_request(mapping))

    return request

  def _create_arrow_packet (self, frames, suppress_errors, on_duplicate_keys,
                            column_mappings):
    request = data_proto.UploadArrowMultiDataRequest()
    for frame in frames:
      request.frame_name.append(frame.encode('utf-8'))
    request.suppress_errors = suppress_errors
    request.on_duplicate_keys = on_duplicate_keys
    request.implicit_vertices = True

    if column_mappings is not None:
      for frame, mapping in column_mappings.items():
        _validate_column_mapping_in_ingest(mapping)
        request.column_mappings[frame].CopyFrom(
          _set_column_mapping_in_ingest_request(mapping))

    return request

  def _insert_csv_packet_generator(self, frames, paths, header_mode,
                                   delimiter, suppress_errors, on_duplicate_keys,
                                   column_mappings):
    request = self._create_csv_packet(frames, paths, header_mode,
                                      delimiter, suppress_errors,
                                      on_duplicate_keys, column_mappings)
    for fpath in paths:
        try:
          data = ''
          dsize = 0
          with open(fpath, 'rb') as f:
            line = f.readline()
            while line:
              line = line.decode('utf-8')
              lsize = len(line)
              if (dsize + lsize) < MAX_PACKET_SIZE:
                data += line
                dsize += lsize
              else:
                request.file_path = fpath
                request.content = data.encode('utf-8')
                yield request
                data = line
                dsize = len(data)
              line = f.readline()
            request.file_path = fpath
            request.content = data.encode('utf-8')
            yield request
        except:
          # Print the error and don't throw since grpc will give an unknown
          # error.
          sys.stderr.write(f"Error in {fpath}: ")
          traceback.print_exc(file = sys.stderr)
          sys.stderr.write("\n")
          pass

  def _insert_arrow_packet_generator(self, frames, paths, suppress_errors,
                                     on_duplicate_keys, column_mappings,
                                     chunk_size):
    request = self._create_arrow_packet(frames, suppress_errors,
                                        on_duplicate_keys, column_mappings)
    for path in paths:
      try:
          file = pyarrow.parquet.ParquetFile(path)
          batches = file.iter_batches(batch_size = chunk_size)
          num_batches = 0
          for batch in batches:
            num_batches += 1
          request.num_batches.append(num_batches)
      except:
        # Print the error and don't throw since grpc will give an unknown
        # error.
        sys.stderr.write(f"Error in {path}: ")
        traceback.print_exc(file = sys.stderr)
        sys.stderr.write("\n")
        pass

    for path in paths:
      try:
          file = pyarrow.parquet.ParquetFile(path)
          batches = file.iter_batches(batch_size = chunk_size)
          for batch in batches:
            sink = pyarrow.BufferOutputStream()
            writer = pyarrow.ipc.new_stream(sink, batch.schema)
            writer.write_batch(batch)
            writer.close()

            # Get the bytes
            buf = sink.getvalue()
            bytes_data = buf.to_pybytes()
            request.content = bytes_data
            yield request
      except:
        # Print the error and don't throw since grpc will give an unknown
        # error.
        sys.stderr.write(f"Error in {path}: ")
        traceback.print_exc(file = sys.stderr)
        sys.stderr.write("\n")
        pass

  def _create_ingest_error_message(self, frames, job):
    num_errors = job.total_ingest_errors

    error_string = 'Errors occurred when inserting data into frames '
    for frame in frames:
      error_string += f'{frame},'
    error_string += '\n'

    error_string += f'  {num_errors} line'
    if num_errors > 1:
      error_string += 's'

    error_string += (' had insertion errors.\n'
                     '  Lines without errors were inserted into the frames.\n'
                     '  To see the number of rows in a frame, run "'
                     'frame_name.num_rows".\n'
                     '  To see the data in the frame, run "'
                     'frame_name.get_data()".\n')

    extra_text = ''
    if num_errors > 10:
      extra_text = ' first 10'

    error_string += (f'Errors associated with the{extra_text} lines '
                     'that could not be inserted are shown below:')

    # Only print the first 10 messages.
    for error in job.get_ingest_errors(0, 10):
      delim = ','

      # Will process a list of strings. Convert to this format.
      if isinstance(error, str):
        error_cols = error.split(delim)
      elif isinstance(error, list):
        error_cols = [str(elem) for elem in error]
      else:
        raise XgtIOError("Error processing ingest error message.")

      # The first comma separated fields of the error string are the error
      # description, file name, and line number.
      error_explanation = "" if len(error_cols) < 1 else error_cols[0]
      error_file_name = \
          "" if len(error_cols) < 2 else os.path.basename(error_cols[1])
      error_line_number = "" if len(error_cols) < 3 else error_cols[2]

      # The second part of the error string contains the line that caused the
      # error. The line contains comma separated fields so we need to re-join
      # these comma separated portions to get back the line.
      line_with_error = \
          "" if len(error_cols) < 4 else delim.join(error_cols[3:])

      if error_line_number == -1:
        error_string += f"\n {error_explanation}"
      else:
        error_string += (f"\n  File: {error_file_name}: Line: "
                         f"{error_line_number}: {error_explanation}")

    return error_string

  def _convert_frame_path_dictionary(self, frames_to_paths):
    # Sort the list of frames to paths to get vertex frames first.
    frames_paths_array = [ (frame_name, path_list)
                           for frame_name, path_list in frames_to_paths.items() ]

    return sorted(frames_paths_array,
                  key = lambda fp : not isinstance(self.get_frame(fp[0]),
                                                   VertexFrame))

  def _replicate_frame_path_array(self, frames_paths_array):
    frames = []
    paths = []
    # Replicate the frame name ONCE per path...
    for frame_name, path_list in frames_paths_array:
      for path in path_list:
        paths.append(path)
        frames.append(frame_name)
    return (frames, paths)

  def _load_multi_frames(self, frames_to_paths, header_mode = HeaderMode.NONE,
                         delimiter = ',', suppress_errors = True,
                         on_duplicate_keys = 'skip', column_mappings = None,
                         chunk_size = DEFAULT_CHUNK_SIZE):
    frames_to_server_paths = { }
    frames_to_csv_paths = { }
    frames_to_parquet_paths = { }

    for frame_name, path_list in frames_to_paths.items():
      client_paths, server_paths, url_paths = _group_paths(path_list, True)
      if (len(client_paths) == 0 and len(server_paths) == 0 and
          len(url_paths) == 0):
        raise XgtIOError(f'no valid paths found: {str(path_list)}')

      server_paths.extend(url_paths)

      if len(client_paths) > 0:
        final_paths = []
        # If any paths have * or ? etc, try to expand those cases to real files.
        for path in client_paths:
          glob_paths = glob.glob(path)
          final_paths += glob_paths if glob_paths != [] else [path]

        client_parquet_paths, client_other_paths = _split_local_paths(final_paths)
        if len(client_other_paths) > 0:
          frames_to_csv_paths[frame_name] = client_other_paths
        if len(client_parquet_paths) > 0:
          frames_to_parquet_paths[frame_name] = client_parquet_paths

      if len(server_paths) > 0:
        frames_to_server_paths[frame_name] = server_paths

    server_paths = self._convert_frame_path_dictionary(frames_to_server_paths)
    client_csv_paths = self._convert_frame_path_dictionary(frames_to_csv_paths)
    client_parquet_paths = self._convert_frame_path_dictionary(
      frames_to_parquet_paths)

    server_frames, server_paths = self._replicate_frame_path_array(server_paths)
    client_parquet_frames, client_parquet_paths = self._replicate_frame_path_array(
      client_parquet_paths)
    client_csv_frames, client_csv_paths = self._replicate_frame_path_array(
      client_csv_paths)

    job_csv = None
    job_parquet = None
    job_server = None

    if len(client_csv_paths) > 0:
      data_iter = self._insert_csv_packet_generator(client_csv_frames,
                                                    client_csv_paths,
                                                    header_mode,
                                                    delimiter, suppress_errors,
                                                    on_duplicate_keys,
                                                    column_mappings)
      response = self._call(data_iter, self._data_svc.UploadCSVMultiData)
      job_csv = Job(self, response.job_status)

    if len(client_parquet_paths) > 0:
      data_iter = self._insert_arrow_packet_generator(client_parquet_frames,
                                                      client_parquet_paths,
                                                      suppress_errors,
                                                      on_duplicate_keys,
                                                      column_mappings,
                                                      chunk_size)
      response = self._call(data_iter, self._data_svc.UploadArrowMultiData)
      job_parquet = Job(self, response.job_status)

    if len(server_paths) > 0:
      requests = []
      for frame, path in zip(server_frames, server_paths):
        request = data_proto.IngestUriRequest()
        request.frame_name = frame
        _, server_path, url_path = _group_paths(path, True)

        if len(server_path) > 0:
          path = server_path
        elif len(url_path) > 0:
          path = url_path

        if isinstance(path, (list, tuple)):
          request.content_uri.extend(path)
        else:
          request.content_uri.extend([path])

        _convert_header_mode(header_mode, request)
        request.implicit_vertices = True
        request.delimiter = delimiter
        request.suppress_errors = suppress_errors
        request.on_duplicate_keys = on_duplicate_keys
        if column_mappings is not None:
          column_mapping = column_mappings[frame]
          _validate_column_mapping_in_ingest(column_mapping)
          request.column_mapping.CopyFrom(
            _set_column_mapping_in_ingest_request(column_mapping))

        requests.append(request)
      response = self._call(iter(requests), self._data_svc.IngestUri)
      job_server = Job(self, response.job_status)

    if job_csv is not None:
      job_data = job_csv.get_ingest_errors()
      if job_data is not None and len(job_data) > 0:
        raise XgtIOError(self._create_ingest_error_message(client_csv_frames, job_csv),
                         job = job_csv)

    if job_parquet is not None:
      job_data = job_parquet.get_ingest_errors()
      if job_data is not None and len(job_data) > 0:
        raise XgtIOError(self._create_ingest_error_message(client_parquet_frames, job_parquet),
                         job = job_parquet)

    if job_server is not None:
      job_data = job_server.get_ingest_errors()
      if job_data is not None and len(job_data) > 0:
        raise XgtIOError(self._create_ingest_error_message(server_frames, job_server),
                         job = job_server)

    return (job_csv, job_parquet, job_server)
