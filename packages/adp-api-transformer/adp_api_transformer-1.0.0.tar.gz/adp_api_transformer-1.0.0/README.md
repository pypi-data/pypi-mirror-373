# adp-api-converter

A utility to transform your OpenAPI specifications (JSON or YAML) for use in the ADP1 APIM repository.  
This tool ensures your API specs have required attributes and outputs a modified OpenAPI JSON file.

## Features

- Accepts OpenAPI specs in `.json`, `.yaml`, or `.yml` formats.
- Adds missing `operationId` and `summary` fields to operations.
- Ensures the `info.title` field is set to a template value.
- Outputs the modified spec as formatted JSON.

## Usage

You can run the converter as a command-line tool:

```sh
adp-api-converter <input_file> [output_file]
```

- `<input_file>`: Path to your OpenAPI spec (YAML or JSON).
- `[output_file]`: (Optional) Path for the output JSON file. Defaults to `openapi.json`.

### Example

```sh
adp-api-converter api.yaml modified_api.json
```

## How it works

- Loads the OpenAPI spec from the provided file.
- Adds or updates the following:
  - `info.title` is set to `{{apiTitle}}`.
  - Each operation gets an `operationId` (if missing) in the format: `<method>_<path>-{consumerphase}`.
  - Each operation gets a `summary` (if missing) in the format: `<METHOD> <path>`.
- Saves the modified spec as JSON.

## Requirements

- Python 3.9+
- [pyyaml](https://pypi.org/project/PyYAML/)