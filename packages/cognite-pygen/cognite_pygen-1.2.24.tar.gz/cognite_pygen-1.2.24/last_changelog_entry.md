
### Fixed

- Generating an SDK for a data model that has a edge with properties
that points to a view that is not in the model no longer raise a
`KeyError`. Instead the user gets a warning and the edge is skipped.