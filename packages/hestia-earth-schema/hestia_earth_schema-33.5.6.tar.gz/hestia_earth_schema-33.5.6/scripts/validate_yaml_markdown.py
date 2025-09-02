import os
import sys
import glob
import re
from functools import reduce
import yaml

FOLDER = './yaml'


def _load_class(filepath: str):
    with open(filepath, 'r') as f:
        return yaml.load(f).get('class')


def _flatten(values: list): return list(reduce(lambda x, y: x + (y if isinstance(y, list) else [y]), values, []))


def _validate_uniqueArrayItem_property(property: dict):
    related_type = property.get('type').replace('Ref[', '').replace('List[', '').replace(']', '')
    related_data = _load_class(os.path.join(FOLDER, f"{related_type}.yaml"))
    related_keys = [p.get('name') for p in related_data.get('properties', [])]

    unique_properties = property.get('uniqueArrayItem', [])
    # TODO: handle recursion
    unique_keys = [k.split('.')[0].replace("'", '') for k in unique_properties]
    return [
        f"{property.get('name')}: '{key}' does not exist for {related_type}" for key in unique_keys if key != '@id' and key not in related_keys
    ]


def _validate_uniqueArrayItem(data: dict):
    properties = [p for p in data.get('properties', []) if len(p.get('uniqueArrayItem', [])) > 0]
    return _flatten(map(_validate_uniqueArrayItem_property, properties))


def _is_valid_md(content: str):
    return len(re.findall(r'\](\s|,|\.)', content)) != 0


def _validate_links(data: dict):
    contents = [data.get('doc')] + [p.get('doc') for p in data.get('properties', [])]
    return list(filter(_is_valid_md, contents))


def main():
    files = glob.glob(os.path.join(FOLDER, '*.yaml'))

    exit_code = ''

    for filepath in files:
        data = _load_class(filepath)

        errors = _validate_links(data)
        if len(errors) > 0:
            err = '\n\t'.join(errors)
            exit_code += f"\nInvalid markdown link in '{filepath}':\n\t{err}"

        errors = _validate_uniqueArrayItem(data)
        if len(errors) > 0:
            err = '\n\t'.join(errors)
            exit_code += f"\nInvalid uniqueArrayItem config in '{filepath}':\n\t{err}"

    sys.exit(0 if exit_code == '' else exit_code)


if __name__ == '__main__':
    main()
