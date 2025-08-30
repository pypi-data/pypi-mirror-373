from __future__ import annotations
from ruamel import yaml
from ruamel.yaml import YAML

from gdcmd.helm.values import ValuesYaml
from gdcmd.helm.values_parser import merge_yaml_strings


def validate(values: tuple[str]):
    yaml_files: list[str] = []
    for value in values:
        try:
            yaml.load(open(value, 'r'))
            yaml_files.append(value)
        except yaml.YAMLError as e:
            print(f"YAML parsing error in values file '{value}': {e}")

    try:
        validate_strings(yaml_files)
    except Exception as e:
        print(f"Validation error: {e}")


def validate_strings(values: list[str]):
    if len(values) == 0:
        print("No values provided for validation.")
        return
    elif len(values) == 1:
        if values[0].strip() == "":
            merged = {}
        else:
            merged = YAML().load(values[0])
    else:
        merged = merge_yaml_strings(*values)

    ValuesYaml().merge_dict(merged)
