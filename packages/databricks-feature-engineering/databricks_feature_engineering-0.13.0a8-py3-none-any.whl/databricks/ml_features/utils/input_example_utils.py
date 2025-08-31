from mlflow.models import ModelSignature
from pyspark.sql.types import Row


def infer_input_example(df_head: Row, signature: ModelSignature) -> dict:
    inputs = signature.inputs
    df_dict = df_head.asDict()

    # mlflow 2.20.2 does validation on the input_example using the signature, and they treat python int as numpy int64, causing the validation to fail if the schema is using int32
    # we need to cast the input_example to be the correct type using the signature
    input_example = {
        colspec.name: colspec.type.to_numpy().type(df_dict[colspec.name])
        for colspec in inputs
        if colspec.name in df_dict
    }

    return input_example
