# adp-api-converter

A utility to transform your OpenAPI specifications (JSON or YAML) for use in the ADP1 APIM repository.  
This tool ensures your API specs have required attributes and outputs a modified OpenAPI JSON file.

## Features

- Accepts OpenAPI specs in `.json`, `.yaml`, or `.yml` formats.
- Adds missing `operationId` and `summary` fields to operations.
- Ensures the `info.title` field is set to a template value.
- **Splits the OpenAPI spec into multiple files based on tags, with paths starting after the tag.**
- Outputs the modified spec as formatted JSON.

## Usage

You can run the converter as a command-line tool:

```sh
python -m adp_api_transformer <input_file> [output_file_or_dir] [--split-by-tag]
```

- `<input_file>`: Path to your OpenAPI spec (YAML or JSON).
- `[output_file_or_dir]`: (Optional) Path for the output JSON file, or output directory if using `--split-by-tag`. Defaults to `openapi.json`.
- `--split-by-tag`: (Optional) Split the OpenAPI spec into multiple files by tag.

### Examples

**Convert and output a single JSON file:**
```sh
python -m adp_api_transformer api.yaml modified_api.json
```

**Split by tag and output to a directory:**
```sh
python -m adp_api_transformer api.yaml output_dir --split-by-tag
```

This will create one file per tag (e.g., `collection.openapi.json`), with each file containing only the paths for that tag.  
**The paths in each split file start after the tag segment.**  
For example, `/collection` becomes `/`, `/collection/{id}` becomes `/{id}`.

## How it works

- Loads the OpenAPI spec from the provided file.
- Adds or updates the following:
  - `info.title` is set to `{{apiTitle}}`.
  - Each operation gets an `operationId` (if missing) in the format: `<method>_<path>-{consumerphase}`.
  - Each operation gets a `summary` (if missing) in the format: `<METHOD> <path>`.
  - Each operation gets a `tags` field (if missing), using the first path segment as the tag.
- If `--split-by-tag` is used:
  - The spec is split into multiple files, one per tag.
  - In each split file, the path starts after the tag segment (e.g., `/collection` → `/`).
- Saves the modified spec(s) as JSON.

## Requirements

- Python 3.9+
- [pyyaml](https://pypi.org/project/PyYAML/)