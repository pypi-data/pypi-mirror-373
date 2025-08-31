# This file is copied as an artifact when Feature Store Client log the model
# during Feature Serving Endpoint creation.
import mlflow

NAN = float("nan")


class IdentityModel(mlflow.pyfunc.PythonModel):
    def __init__(self) -> None:
        super().__init__()
        self._is_databricks_internal_feature_serving_model = True

    def __eq__(self, __o: object) -> bool:
        """All IdentityModels are equal"""
        return isinstance(__o, IdentityModel)

    def predict(self, ctx, input_df):
        return input_df.replace(NAN, None)
