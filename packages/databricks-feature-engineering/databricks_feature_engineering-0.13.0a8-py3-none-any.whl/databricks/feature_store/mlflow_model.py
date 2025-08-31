import os
from typing import Any, Dict, Optional, Union

import mlflow
import pandas as pd
from pyspark.sql import DataFrame, SparkSession

from databricks.feature_engineering.client import FeatureEngineeringClient
from databricks.ml_features._spark_client._spark_client import SparkClient
from databricks.ml_features.constants import MODEL_DATA_PATH_ROOT
from databricks.ml_features.utils import request_context
from databricks.ml_features_common.mlflow_model_constants import _NO_RESULT_TYPE_PASSED


class _FeatureStoreModelWrapper:
    def __init__(self, path: str):
        self.path = path
        self.fe = FeatureEngineeringClient()
        # defaults to double type since it is the default type for fe.score_batch()
        self.result_type = "double"
        self.use_spark_native_join = False

    def predict(
        self,
        df: Union[DataFrame, pd.DataFrame],
        params: Optional[Dict[str, Any]] = None,
    ) -> DataFrame:

        is_pandas_df = isinstance(df, pd.DataFrame)
        if is_pandas_df:
            spark_client = SparkClient()
            df = spark_client.createDataFrame(df, None)

        # Models logged before this change will not have a params attribute
        # _NO_RESULT_TYPE_PASSED is the default value passed by predict for result_type,
        # which we don't want to pass to score_batch
        if (
            params
            and params.get("result_type", _NO_RESULT_TYPE_PASSED)
            != _NO_RESULT_TYPE_PASSED
        ):
            self.result_type = params.get("result_type")
        score_batch_dataframe = self.fe._training_scoring_client.score_batch(
            model_uri=None,
            df=df,
            result_type=self.result_type,
            client_name=request_context.MLFLOW_CLIENT,
            local_uri=self.path,
            use_spark_native_join=self.use_spark_native_join,
        )
        predictions = score_batch_dataframe.select("prediction")
        if is_pandas_df:
            predictions = predictions.toPandas()
        return predictions

    def set_result_type(self, result_type: str):
        self.result_type = result_type

    def set_use_spark_native_join(self, use_spark_native_join: bool):
        self.use_spark_native_join = use_spark_native_join


def _load_pyfunc(path):
    # Path provided by mlflow is subdirectory of path needed by score_batch
    artifact_path = os.path.join(mlflow.pyfunc.DATA, MODEL_DATA_PATH_ROOT)
    index = path.find(artifact_path)
    return _FeatureStoreModelWrapper(path[:index])
