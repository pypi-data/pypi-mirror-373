from typing import Any

import numpy as np

from databricks.ml_features_common.entities.data_type import DataType

# TODO: Add support for timestamp and date types
# - Decimal: currently not supported because model serving does not support it
# - Date, Timestamp: currently not supported because of PyYAML's "smart" parsing of dates and timestamp strings that breaks protobuf's ParseDict


def deserialize_default_value_to_data_type(
    value_string: str, data_type: DataType
) -> Any:
    """
    Deserialize a default value string representation to the specified data type.
    :param value_string: The string representation of the default value.
    :param data_type: The data type to which the value should be deserialized.
    :return: The deserialized value in the specified data type.
    """
    if not value_string or not data_type:
        return None

    if data_type == DataType.INTEGER:
        return np.int32(value_string)
    elif data_type == DataType.LONG:
        return np.int64(value_string)
    elif data_type == DataType.SHORT:
        return np.int16(value_string)
    elif data_type == DataType.FLOAT:
        return np.float32(value_string)
    elif data_type == DataType.DOUBLE:
        return np.float64(value_string)
    elif data_type == DataType.BOOLEAN:
        return value_string.lower() == "true"
    elif data_type == DataType.STRING:
        return value_string
    else:
        raise ValueError(f"Unsupported data type: {data_type} for default value")


def deserialize_default_value_primitive_type(
    value_string: str, data_type: DataType
) -> Any:
    """
    Deserialize a default value string representation to the specified Python primitive data types.
    :param value_string: The string representation of the default value.
    :param data_type: The data type to which the value should be deserialized.
    :return: The deserialized value in the specified Python data type.
    """
    if not value_string or not data_type:
        return None

    if (
        data_type == DataType.INTEGER
        or data_type == DataType.LONG
        or data_type == DataType.SHORT
    ):
        return int(value_string)
    elif data_type == DataType.FLOAT or data_type == DataType.DOUBLE:
        return float(value_string)
    elif data_type == DataType.BOOLEAN:
        return value_string.lower() == "true"
    elif data_type == DataType.STRING:
        return value_string
    else:
        raise ValueError(f"Unsupported data type: {data_type} for default value")


def serialize_default_value(value: Any) -> str:
    """
    Serialize a default value to its string representation.
    :param value: The default value to serialize.
    :return: The string representation of the default value.
    """
    if value is None:
        return ""
    elif isinstance(value, str):
        return value
    elif isinstance(
        value,
        (
            int,
            float,
            bool,
            np.int16,
            np.int32,
            np.int64,
            np.float32,
            np.float64,
        ),
    ):
        return str(value)
    else:
        raise ValueError(
            f"Unsupported type for default value serialization: {type(value)}"
        )
