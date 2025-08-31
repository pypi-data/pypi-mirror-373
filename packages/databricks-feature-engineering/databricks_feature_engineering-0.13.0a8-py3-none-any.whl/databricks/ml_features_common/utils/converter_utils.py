import json
from abc import ABC, abstractmethod
from typing import Dict, Union

import numpy as np

from databricks.ml_features_common.entities.online_feature_table import (
    FeatureDetails,
    PrimaryKeyDetails,
)
from databricks.ml_features_common.protos.feature_store_serving_pb2 import (
    DataType as ProtoDataType,
)


# Abstract base class for converters
class Converter(ABC):
    pass


# Helper functions for converter decorators
def __validate_value(converter, args, kwargs):
    """
    Validate the value parameter passed into the converter function.
    :param converter: Static or non-static function.
    :param args: Positional arguments passed into the converter function.
    :param kwargs: Keyword arguments passed into the converter function.
    :return: True if value is valid; otherwise, False. If value is valid, returns the value as tuple
    """

    # If it is a stateful converter then first argument will always be self
    if len(args) > 0 and isinstance(args[0], Converter):
        non_self_args = args[1:]
    else:
        non_self_args = args

    # Input is invalid if both positional arguments (args) and keyword arguments (kwargs) are provided,
    # or if keyword arguments (kwargs) are provided with keyword other than value,
    # as it becomes ambiguous to determine the intended value.
    if len(non_self_args) + len(kwargs) != 1 or (
        len(kwargs) == 1 and "value" not in kwargs
    ):
        return False, None

    if "value" in kwargs:
        return True, kwargs["value"]
    else:
        return True, non_self_args[0]


def return_if_none(converter):
    """
    Decorator to return None early if the value parameter passed into converter function is None.
    :param converter: Static or non-static function.
    :return: None if input is None; otherwise, converted value.
    """

    def inner(*args, **kwargs):
        # This function expects either one positional argument or one keyword argument with name
        # "value".
        # Perform validation on kwargs and args before applying the None logic, this way if the user
        # incorrectly passes in wrong arguments we can rely on the underlying logic of converter
        # function to catch the errors.
        is_valid_value, value = __validate_value(converter, args, kwargs)
        if is_valid_value and value is None:
            return None

        return converter(*args, **kwargs)

    return inner


def return_if_nan(converter):
    """
    Decorator to return np.nan if the value parameter passed into the converter function is np.nan.
    This is used for the numpy.int16/32/64 types, as np.nan is not a valid constructor input for int types.

    TODO (ML-20967): Determine what represents a empty value in online lookup and update this decorator.
    """

    def inner(*args, **kwargs):
        """
        We currently use np.nan to represent missing values from the online store.
        np.nan is a float type and can't be coerced to a np.int16/32/64.
        In ML nan is usually used to represent missing values.
        """
        # This function expects either one positional argument or one keyword argument with name
        # "value".
        # Perform validation on kwargs and args before applying the Nan logic, this way if the user
        # incorrectly passes in wrong arguments we can rely on the underlying logic of converter
        # function to catch the errors.
        is_valid_value, value = __validate_value(converter, args, kwargs)
        if is_valid_value and isinstance(value, float) and np.isnan(value):
            return np.nan

        return converter(*args, **kwargs)

    return inner


class ConverterFactory:
    """
    ConverterFactory exposes a single factory method `get_converter` to generate a converter
    for the data type of the given feature/primary key.
    There should be a ConverterFactory instance defined for each online store.
    See `dynamodb_type_utils.py` for example usage.
    """

    def __init__(self, basic_datatype_converters, complex_datatype_converters):
        # Both inputs are dictionary of data type -> converter mapping for this online store.
        # See `dynamodb_type_utils.py` for example usage.
        self._basic_datatype_converters = basic_datatype_converters
        self._complex_datatype_converters = complex_datatype_converters

    def get_converter(self, details: Union[FeatureDetails, PrimaryKeyDetails]):
        # Looks up the data type converter subclass based on the input FeatureDetails or PrimaryKeyDetails.
        data_type_details = (
            json.loads(details.data_type_details)
            if isinstance(details, FeatureDetails) and details.data_type_details
            else None
        )
        return self._get_converter_detailed(
            data_type=details.data_type, details=data_type_details
        )

    def _get_converter_detailed(self, data_type, details: Union[str, Dict]):
        if data_type in self._basic_datatype_converters:
            return self._basic_datatype_converters[data_type]
        elif data_type in self._complex_datatype_converters and details:
            return self._complex_datatype_converters[data_type](
                details, self._get_converter_detailed
            )
        raise ValueError(
            f"Internal Error: Unsupported data type: {ProtoDataType.Name(data_type)}, details='{details}'"
        )
