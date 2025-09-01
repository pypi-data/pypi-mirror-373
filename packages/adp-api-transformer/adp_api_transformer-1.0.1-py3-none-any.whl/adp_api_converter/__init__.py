import sys
import json
import yaml
import argparse
import os
from copy import deepcopy

def load_spec(file_path):
    with open(file_path, 'r') as f:
        if file_path.endswith(('.yaml', '.yml')):
            return yaml.safe_load(f)
        elif file_path.endswith('.json'):
            return json.load(f)
        else:
            raise ValueError("Unsupported file format. Please provide a .json or .yaml file.")

def generate_operation_id(method, path):
    clean_path = path.strip('/').replace('/', '_').replace('{', '').replace('}', '')
    return f"{method}_{clean_path}"+"-{{consumerphase}}"

def add_missing_attributes(spec):
    if 'info' not in spec or not isinstance(spec['info'], dict):
        spec['info'] = {}
    spec['info']['title'] = '{{apiTitle}}'

    paths = spec.get('paths', {})
    for path, methods in paths.items():
        for method, operation in methods.items():
            if not isinstance(operation, dict):
                continue
            if 'operationId' not in operation:
                operation['operationId'] = generate_operation_id(method, path)
            if 'summary' not in operation:
                operation['summary'] = f"{method.upper()} {path}"
            # Add a default tag if missing, using the first path segment
            if 'tags' not in operation or not operation['tags']:
                first_segment = path.strip('/').split('/')[0]
                operation['tags'] = [first_segment]
    return spec

def save_as_json(spec, output_path):
    with open(output_path, 'w') as f:
        json.dump(spec, f, indent=2)

def split_openapi_by_tag(spec):
    """
    Splits the OpenAPI spec into multiple specs based on the first tag of each operation.
    The path in each split spec starts after the tag segment, or '/' if the tag is the last segment.
    """
    tag_specs = {}

    for path, methods in spec.get("paths", {}).items():
        for method, operation in methods.items():
            if not isinstance(operation, dict):
                continue
            tags = operation.get("tags", [])
            if not tags:
                continue
            tag = tags[0]
            tag_lower = tag.lower()
            parts = path.strip('/').split('/')
            try:
                tag_index = [p.lower() for p in parts].index(tag_lower)
                # If tag is the last segment, use '/'
                if tag_index == len(parts) - 1:
                    new_path = '/'
                else:
                    # new_path is everything after the tag (exclusive)
                    new_parts = parts[tag_index + 1 :]
                    new_path = '/' + '/'.join(new_parts)
            except ValueError:
                new_path = path

            if tag not in tag_specs:
                tag_specs[tag] = deepcopy(spec)
                tag_specs[tag]["paths"] = {}

            if new_path not in tag_specs[tag]["paths"]:
                tag_specs[tag]["paths"][new_path] = {}
            tag_specs[tag]["paths"][new_path][method] = deepcopy(operation)

    return tag_specs

def save_split_specs(spec, output_dir):
    """
    Splits the OpenAPI spec and saves each tag spec as a JSON file in the output directory.
    """
    os.makedirs(output_dir, exist_ok=True)
    tag_specs = split_openapi_by_tag(spec)
    for tag, tag_spec in tag_specs.items():
        filename = f"{tag.lower()}.openapi.json"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(tag_spec, f, indent=2)

def convert_api_spec():
    parser = argparse.ArgumentParser(description="Modify OpenAPI spec and output as JSON, or split by tag.")
    parser.add_argument("input_file", help="Path to the input OpenAPI spec file (JSON or YAML).")
    parser.add_argument("output", nargs='?', default="openapi.json", help="Output file or directory.")
    parser.add_argument("--split-by-tag", action="store_true", help="Split the OpenAPI spec by tag into multiple files.")
    args = parser.parse_args()
    input_path = os.path.abspath(args.input_file)
    output_path = os.path.abspath(args.output)
    spec = load_spec(input_path)
    modified_spec = add_missing_attributes(spec)
    if args.split_by_tag:
        save_split_specs(modified_spec, input_path.split('.')[0])
        print(f"OpenAPI spec split by tag and saved to directory {input_path.split('.')[0]}")
    else:
        save_as_json(modified_spec, output_path)
        print(f"Modified OpenAPI spec saved to {output_path}")