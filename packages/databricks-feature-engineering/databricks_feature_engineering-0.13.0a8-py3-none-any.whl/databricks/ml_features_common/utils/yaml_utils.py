import codecs
import os
from typing import Any, Dict, Optional

from yaml import dump, load

try:
    from yaml import CSafeDumper as SafeDumper
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeDumper, SafeLoader


ENCODING = "utf-8"
SAFE_DUMPER = SafeDumper


def read_yaml(path: str, file_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Reads a YAML file and returns the data as a dictionary.
    :param path: Path to the YAML file.
    :param file_name: Name of the YAML file. If None, it assume the path param
    :return: Dictionary containing the data from the YAML file.
    """
    full_file_name = os.path.join(path, file_name) if file_name else path
    with open(full_file_name, "r", encoding=ENCODING) as file:
        data = load(file, Loader=SafeLoader)
    return data


def write_yaml(path: str, file_name: str, data_dict: Dict[str, Any]):
    """
    Writes a dictionary to a YAML file.
    :param path: Path to the YAML file.
    :param file_name: Name of the YAML file.
    :param data_dict: Dictionary containing the data to write.
    """
    full_file_name = os.path.join(path, file_name)
    with codecs.open(full_file_name, mode="w", encoding=ENCODING) as yaml_file:
        dump(
            data_dict,
            yaml_file,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            Dumper=SafeDumper,
        )
