import os
import json
import shutil
from pathlib import Path
from datamodel_code_generator import generate

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.join(_CURRENT_DIR, '..')
_SRC_DIR = os.path.join(_ROOT_DIR, 'src', '@hestia-earth', 'json-schema', 'json-schema')

_TMP_DIR = os.path.join(_CURRENT_DIR, 'pydantic')
_DEST_DIR = os.path.join(_ROOT_DIR, 'hestia_earth', 'schema', 'pydantic')


def _clean_dir(folder: str):
    os.makedirs(folder, exist_ok=True)
    shutil.rmtree(folder)
    os.makedirs(folder, exist_ok=True)


def _remove_deep_ref(value: dict):
    if 'items' in value and '$ref' in value['items']:
        value['items']['$ref'] = value['items']['$ref'].replace('-deep', '')
    if '$ref' in value:
        value['$ref'] = value['$ref'].replace('-deep', '')

    return value


def _copy_schema(file: str):
    with open(os.path.join(_SRC_DIR, file), 'r') as f:
        data = json.load(f)

    data['$id'] = f"{data['title']}.json"

    # replace all -deep references
    data['properties'] = {
      k: _remove_deep_ref(v)
      for k, v in data['properties'].items()
    }

    with open(os.path.join(_TMP_DIR, file), 'w') as f:
        f.write(json.dumps(data, indent=2))


def main():
  _clean_dir(_TMP_DIR)
  _clean_dir(_DEST_DIR)

  files = [f for f in os.listdir(_SRC_DIR) if not 'deep' in f]

  # copy files for pydantic
  list(map(_copy_schema, files))

  generate(
      input_=Path(_TMP_DIR),
      input_file_type="json_schema",
      output=Path(_DEST_DIR),
      custom_formatters=['formatters.float', 'formatters.dates'],
      custom_template_dir=Path(os.path.join(_CURRENT_DIR, 'templates'))
    )


if __name__ == '__main__':
    main()
