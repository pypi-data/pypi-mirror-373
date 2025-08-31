from unittest.mock import MagicMock

from pyspark.sql import DataFrame

# TODO (ML-30526): Move this file to the tests module.


def mock_pyspark_dataframe(**kwargs):
    df = MagicMock(spec=DataFrame)
    df.configure_mock(**kwargs)
    df.isStreaming = False
    return df
