import os
import sys
import re
import json
import yaml
import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows

# This is a sample Python script to covert yaml files to an Excel spreadsheet.
YAML_DIR = './yaml'
with open('./package.json', 'r') as f:
    VERSION = json.load(f)['version']


def clean_description(description: str):
    for match in re.findall('\\[[^\\]]*\\]' '\\(.+?\\)', description):
        part_1 = re.findall('\\[[^\\]]*\\]', match)
        part_1 = part_1[0][1:(len(part_1[0])-1)]
        description = description.replace(match, part_1)
    for match in re.findall('\\[[^\\]]*\\]', description):
        part_1 = match[1:(len(match) - 1)]
        description = description.replace(match, part_1)
    return description


def import_schema(filepath: str):
    """Function that generates HESTIA nodes excel representations in a dynamic way, directly from yaml files.
        Arguments:
            filepath: The path to a HESTIA schema node defined in a yaml file.
        Returns a dictionary that represents the HESTIA node."""

    with open(filepath) as yaml_file:
        schema_bulk = yaml.load(yaml_file, yaml.SafeLoader)

    df = pd.DataFrame(columns=['Node.Field', 'Node', 'Field', 'Type', 'Required', 'enum', 'Description'])

    name = schema_bulk['class']['name']
    description = schema_bulk['class']['doc'] if 'doc' in schema_bulk['class'] else ""
    df.loc[0] = [
        name + '.' + name,
        name,
        name,
        schema_bulk['class']['type'],
        '-',
        '-',
        clean_description(description.strip())
    ]

    counter = 1
    properties = list(filter(
        lambda prop: 'internal' not in prop and 'hidden' not in prop and 'deprecated' not in prop,
        schema_bulk['class']['properties']
    ))
    for prop in properties:
        description = prop['doc'] if 'doc' in prop else "-"
        required = prop['required'] if 'required' in prop else "-"
        enum_values = ','.join(map(lambda x: str(x), prop['enum'])) if 'enum' in prop else "-"
        df.loc[counter] = [
            name + '.' + prop['name'],
            name,
            prop['name'],
            prop['type'],
            str(required),
            enum_values,
            clean_description(description.strip())
        ]
        counter = counter + 1

    return df


def process_nodes(args):
    """Function that generates a summary of HESTIA nodes for all the yaml files in a directory and stores the results
    in an excel file.
        Arguments:
            None
        Returns None."""
    src_filepath = args[0]
    dest_filepath = args[1]
    filenames = os.listdir(YAML_DIR)

    df = None

    for file in filenames:
        node = import_schema(f"{YAML_DIR}/{file}")
        df = node if df is None else df.append(node, ignore_index=True)
        df = df.reindex()

    wb = load_workbook(src_filepath, keep_vba=True)
    ws = wb['schema_list']
    # ws.delete_rows(0) # not working
    for r in dataframe_to_rows(df, index=False, header=True):
        ws.append(r)
    wb.save(f"{dest_filepath.split('.')[0]}-{VERSION}.{dest_filepath.split('.')[1]}")


if __name__ == '__main__':
    process_nodes(sys.argv[1:])
