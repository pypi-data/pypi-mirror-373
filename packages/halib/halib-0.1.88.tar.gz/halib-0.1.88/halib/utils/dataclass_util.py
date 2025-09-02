import yaml
from typing import Any
from rich.pretty import pprint
from ..filetype import yamlfile
# from halib.filetype import yamlfile
from dataclasses import make_dataclass

def dict_to_dataclass(name: str, data: dict):
    fields = []
    values = {}

    for key, value in data.items():
        if isinstance(value, dict):
            sub_dc = dict_to_dataclass(key.capitalize(), value)
            fields.append((key, type(sub_dc)))
            values[key] = sub_dc
        else:
            field_type = type(value) if value is not None else Any
            fields.append((key, field_type))
            values[key] = value

    DC = make_dataclass(name.capitalize(), fields)
    return DC(**values)

def yaml_to_dataclass(name: str, yaml_str: str):
    data = yaml.safe_load(yaml_str)
    return dict_to_dataclass(name, data)


def yamlfile_to_dataclass(name: str, file_path: str):
    data_dict = yamlfile.load_yaml(file_path, to_dict=True)
    if "__base__" in data_dict:
        del data_dict["__base__"]
    return dict_to_dataclass(name, data_dict)

if __name__ == "__main__":
    cfg = yamlfile_to_dataclass("Config", "test/dataclass_util_test_cfg.yaml")

    # ! NOTICE: after print out this dataclass, we can copy the output and paste it into CHATGPT to generate a list of needed dataclass classes using `from dataclass_wizard import YAMLWizard`
    pprint(cfg)
