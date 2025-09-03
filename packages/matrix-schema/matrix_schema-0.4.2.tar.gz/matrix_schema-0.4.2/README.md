# matrix-schema

The collected MATRIX schemas

## Website

[https://everycure-org.github.io/matrix-schema](https://everycure-org.github.io/matrix-schema)

## Repository Structure

* [examples/](examples/) - example data
* [project/](project/) - project files (do not edit these)
* [src/](src/) - source files (edit these)
  * [matrix_schema](src/matrix_schema)
    * [schema](src/matrix_schema/schema) -- LinkML schema
      (edit this)
      * [valid_biolink_edge_types.tsv](src/matrix_schema/schema/valid_biolink_edge_types.tsv) -- Generated table of valid edge types
    * [datamodel](src/matrix_schema/datamodel) -- generated
      Python datamodel
    * [utils](src/matrix_schema/utils) -- utility scripts for schema generation
* [tests/](tests/) - Python tests

## Developer Documentation

<details>
Use the `make` command to generate project artefacts:

* `make all`: make everything
* `make deploy`: deploys site
* `make gen-valid-edge-type-table`: regenerate the valid Biolink edge types table
</details>

## Release Artifacts

The following artifacts are automatically generated and attached to GitHub releases:

* `valid_biolink_edge_types.tsv` - A table of valid edge types from the Biolink model with columns for `subject_category`, `predicate`, and `object_category`

## Credits

This project was made with
[linkml-project-cookiecutter](https://github.com/linkml/linkml-project-cookiecutter).
