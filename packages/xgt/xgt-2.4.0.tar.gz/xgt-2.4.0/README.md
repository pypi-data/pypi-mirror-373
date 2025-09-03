xGT is a high-performance property graph engine designed to support extremely large in-memory graphs, and the `xgt` library is the client-side interface which controls it.

## Documentation

The `xgt` library is self-documenting, and all external methods and classes have docstrings accessible through `help()`.
A formatted version of the same is available online on the Rocketgraph documentation site: [docs.rocketgraph.com](http://docs.rocketgraph.com/).

## Extra Tools

Most users will find installing the following packages useful:

| Package | Description |
| ------- | ----------- |
| jupyter | For an interactive environment to use xgt. |
| pandas  | For importing / exporting data to / from pandas frames. |

The "extra" variant of `xgt` is provided to make installing these useful packages along with xgt easy.  Install by doing: `pip install xgt[extra]`.
