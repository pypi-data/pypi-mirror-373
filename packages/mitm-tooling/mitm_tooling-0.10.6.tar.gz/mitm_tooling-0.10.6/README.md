# mitm-tooling

This python package contains basic functionality to work with "Models-in-the-Middle" (MitM) data sets.
It bundles a generic mechanism to load and export relational data as a configurable MitM.

## Package Structure

- `mitm_tooling/data_types`: Defines the basic attribute data types supported in MitMs.
- `mitm_tooling/definition`: Contains MitM definitions. Currently, only `MAED` is supported.
- `mitm_tooling/extraction/relational`: Functionality for mapping and (virtually) transforming relational databases.
  This is
  used by
  the [maed\[/mitm\]-exporter-backend](https://git-ce.rwth-aachen.de/machine-data/maed-exporter/maed-exporter-backend).
- `mitm_tooling/extraction/anything`: An environment for applying the above to (relatively) arbitrary data sources.
- `mitm_tooling/representation`: Defines different representations of MitM data. From the proposed zipped format to
  dataframes and a relational DB representation.
    - `/sql`: Defines the relational representation along with utilities for inserting any (mapped) MitM data, by
      essentially executing a (streamable) ETL pipeline.
- `mitm_tooling/transformation`: Functionality for converting different representations into each other. Also contains
    - `/superset`: Functionality for generating superset-importable definitions, particularly programmatically defined
      dynamic dashboards. This is used by
      the [superset-mitm-service](https://git-ce.rwth-aachen.de/machine-data/superset-mitm-service).
- `mitm_tooling/io`: Im/Export functionality.
- `mitm_tooling/utilities`: Some utility functions.

For more details, consider the API documentation:

<a href="https://machine-data.pages.git-ce.rwth-aachen.de/mitm-tooling/" style="display:inline-block;padding:10px 20px;background:#0078d4;color:#fff;border-radius:6px;text-decoration:none;font-weight:bold;">
  <img src="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.4.2/svgs/solid/book.svg" alt="API Docs" width="24" height="24" style="vertical-align:middle;margin-right:8px;">
  Package Docs
</a>

## Extension Points

1. Adding new MitMs via a `.yaml` definition.
2. Adding transformation capabilities to/from other formats.
3. Adding new model-specific visualization creators (e.g.,
   `mitm_tooling/transformation/superset/visualizations/maed/dashboards.py`)
4. Extending the relational representation with more mutation capabilities (e.g., instance updates).