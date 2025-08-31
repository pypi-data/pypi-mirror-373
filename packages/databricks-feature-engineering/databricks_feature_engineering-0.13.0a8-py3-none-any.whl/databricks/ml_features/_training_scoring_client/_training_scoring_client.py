import json
import logging
import os
from collections import defaultdict
from types import ModuleType
from typing import Any, Dict, List, Optional, Set, Union

import mlflow
import yaml
from mlflow.models import Model, ModelSignature
from mlflow.utils.file_utils import TempDir
from pyspark.sql import DataFrame
from pyspark.sql.functions import struct

from databricks.ml_features._catalog_client._catalog_client import CatalogClient
from databricks.ml_features._catalog_client._catalog_client_helper import (
    CatalogClientHelper,
)
from databricks.ml_features._databricks_client._databricks_client import (
    DatabricksClient,
)
from databricks.ml_features._information_schema_spark_client._information_schema_spark_client import (
    InformationSchemaSparkClient,
)
from databricks.ml_features._materialization_client._materialization_client import (
    MaterializationClient,
)
from databricks.ml_features._spark_client._spark_client import SparkClient
from databricks.ml_features._spark_client._spark_client_helper import SparkClientHelper
from databricks.ml_features.constants import (
    _PREBUILT_ENV_URI,
    _USE_SPARK_NATIVE_JOIN,
    _WARN,
    MODEL_DATA_PATH_ROOT,
    PREDICTION_COLUMN_NAME,
)
from databricks.ml_features.entities.data_source import DataSource, DeltaTableSource
from databricks.ml_features.entities.feature import Feature
from databricks.ml_features.entities.feature_function import FeatureFunction
from databricks.ml_features.entities.feature_lookup import FeatureLookup
from databricks.ml_features.entities.feature_table import FeatureTable
from databricks.ml_features.entities.training_set import (
    TrainingSet,
    TrainingSetWithDeclarativeFeatures,
)
from databricks.ml_features.utils import (
    input_example_utils,
    request_context,
    training_scoring_utils,
    utils,
    validation_utils,
)
from databricks.ml_features.utils.request_context import RequestContext
from databricks.ml_features.utils.signature_utils import (
    drop_signature_inputs_and_invalid_params,
    get_mlflow_signature_from_feature_spec,
)
from databricks.ml_features.utils.version_compatibility_utils import (
    is_log_model_artifact_path_deprecated,
    mlflow_log_model_starts_run,
)
from databricks.ml_features.version import VERSION
from databricks.ml_features_common import mlflow_model_constants
from databricks.ml_features_common.entities.column_info import ColumnInfo
from databricks.ml_features_common.entities.feature_column_info import FeatureColumnInfo
from databricks.ml_features_common.entities.feature_spec import FeatureSpec
from databricks.ml_features_common.entities.feature_spec_declarative import (
    FeatureSpecDeclarative,
)
from databricks.ml_features_common.entities.source_data_column_info import (
    SourceDataColumnInfo,
)
from databricks.ml_features_common.mlflow_model_constants import _NO_RESULT_TYPE_PASSED
from databricks.ml_features_common.utils import uc_utils, utils_common
from databricks.ml_features_common.utils.feature_spec_utils import (
    assign_topological_ordering,
    convert_to_yaml_string,
    get_encoded_graph_map,
    load_feature_spec,
)
from databricks.ml_features_common.utils.yaml_utils import read_yaml

_logger = logging.getLogger(__name__)

FEATURE_SPEC_GRAPH_MAX_COLUMN_INFO = 1000


class TrainingScoringClient:
    def __init__(
        self,
        catalog_client: CatalogClient,
        catalog_client_helper: CatalogClientHelper,
        spark_client: SparkClient,
        spark_client_helper: SparkClientHelper,
        materialization_client: Optional[MaterializationClient],
        information_schema_spark_client: InformationSchemaSparkClient,
        databricks_client: DatabricksClient,
        model_registry_uri: str,
    ):
        self._catalog_client = catalog_client
        self._catalog_client_helper = catalog_client_helper
        self._spark_client = spark_client
        self._materialization_client = materialization_client
        self._spark_client_helper = spark_client_helper
        self._information_schema_spark_client = information_schema_spark_client
        self._databricks_client = databricks_client
        self._model_registry_uri = model_registry_uri

    def create_training_set(
        self,
        feature_spec: FeatureSpec,
        feature_column_infos: List[FeatureColumnInfo],
        label_names: List[str],
        req_context: RequestContext,
        df: DataFrame,
        ft_metadata: training_scoring_utils._FeatureTableMetadata,
        kwargs,
    ):
        uc_function_infos = training_scoring_utils.get_uc_function_infos(
            self._information_schema_spark_client,
            {odci.udf_name for odci in feature_spec.on_demand_column_infos},
        )

        # TODO(divyagupta-db): Move validation from _validate_join_feature_data in feature_lookup_utils.py
        #  to a helper function called here and in score_batch.

        # Add consumer of each feature and instrument as final step
        consumer_feature_table_map = defaultdict(list)
        for feature in feature_column_infos:
            consumer_feature_table_map[feature.table_name].append(feature.feature_name)
        consumed_udf_names = [f.udf_name for f in feature_spec.function_infos]
        additional_add_consumer_headers = {
            request_context.IS_TRAINING_SET_LABEL_SPECIFIED: str(
                bool(label_names)
            ).lower(),
            request_context.NUM_ON_DEMAND_FEATURES_LOGGED: str(
                len(feature_spec.on_demand_column_infos)
            ),
            # Key by consumed_udf_names for determinism, as it is unique and sorted.
            request_context.NUM_LINES_PER_ON_DEMAND_FEATURE: json.dumps(
                [
                    len(uc_function_infos[udf_name].routine_definition.split("\n"))
                    for udf_name in consumed_udf_names
                    # Routine definition will be None if this user is not the owner
                    # of the UDF. This metric will only be instrumented when the
                    # user is the UDF owner.
                    if uc_function_infos[udf_name].routine_definition is not None
                ]
            ),
        }

        # A graph map representing the graph of column infos in the feature spec.
        # Keys are the encoded columns and values are lists of dependencies.
        if len(feature_spec.column_infos) < FEATURE_SPEC_GRAPH_MAX_COLUMN_INFO:
            additional_add_consumer_headers[
                request_context.FEATURE_SPEC_GRAPH_MAP
            ] = json.dumps(get_encoded_graph_map(feature_spec.column_infos))

        add_consumer_req_context = RequestContext.with_additional_custom_headers(
            req_context, additional_add_consumer_headers
        )
        self._catalog_client_helper.add_consumer(
            consumer_feature_table_map, add_consumer_req_context
        )
        # Spark query planning is known to cause spark driver to crash if there are many feature tables to PiT join.
        # See https://docs.google.com/document/d/1EyA4vvlWikTJMeinsLkxmRAVNlXoF1eqoZElOdqlWyY/edit
        # So we disable native join by default.
        training_scoring_utils.warn_if_non_photon_for_native_spark(
            kwargs.get(_USE_SPARK_NATIVE_JOIN, False), self._spark_client
        )
        return TrainingSet(
            feature_spec,
            df,
            label_names,
            ft_metadata.feature_table_metadata_map,
            ft_metadata.feature_table_data_map,
            uc_function_infos,
            kwargs.get(_USE_SPARK_NATIVE_JOIN, False),
        )

    def create_training_set_from_feature_lookups(
        self,
        df: DataFrame,
        feature_lookups: List[Union[FeatureLookup, FeatureFunction]],
        label: Union[str, List[str], None],
        exclude_columns: List[str],
        client_name: str,
        **kwargs,
    ) -> TrainingSet:
        req_context = RequestContext(request_context.CREATE_TRAINING_SET, client_name)

        # FeatureFunction is allowed as an undocumented type for feature_lookups parameter
        features = feature_lookups
        feature_lookups = [f for f in features if isinstance(f, FeatureLookup)]
        feature_functions = [f for f in features if isinstance(f, FeatureFunction)]

        # Maximum of 100 FeatureFunctions is supported
        if len(feature_functions) > training_scoring_utils.MAX_FEATURE_FUNCTIONS:
            raise ValueError(
                f"A maximum of {training_scoring_utils.MAX_FEATURE_FUNCTIONS} FeatureFunctions are supported."
            )

        # Initialize label_names with empty list if label is not provided
        label_names = utils.as_list(label, [])
        del label

        training_scoring_utils.verify_df_and_labels(df, label_names, exclude_columns)

        ft_metadata = training_scoring_utils.get_table_metadata(
            self._catalog_client,
            self._catalog_client_helper,
            self._spark_client,
            {fl.table_name for fl in feature_lookups},
            req_context,
        )

        column_infos = training_scoring_utils.get_column_infos(
            feature_lookups,
            feature_functions,
            ft_metadata,
            df_columns=df.columns,
            label_names=label_names,
        )

        training_scoring_utils.validate_column_infos(
            self._spark_client_helper,
            self._information_schema_spark_client,
            ft_metadata,
            column_infos.source_data_column_infos,
            column_infos.feature_column_infos,
            column_infos.on_demand_column_infos,
            label_names,
        )

        if client_name == request_context.FEATURE_ENGINEERING_CLIENT:
            # Feature Engineering client moved the FeatureSpec generation logic to the server.
            input_columns = [col for col in df.columns if col not in label_names]
            feature_spec_yaml = self._catalog_client.generate_feature_spec_yaml(
                features,
                exclude_columns,
                input_columns,
                req_context,
            )
            feature_spec = FeatureSpec._from_dict(yaml.safe_load(feature_spec_yaml))
        else:
            if any(
                [
                    hasattr(f, "default_values") and f.default_values
                    for f in feature_lookups
                ]
            ):
                _logger.warning(
                    "FeatureStore Client does not support default values for FeatureLookups, Any specified default values will be ignored. Please use Feature Engineering Client"
                )
                # clear default values from feature lookups
                for feature_lookup in feature_lookups:
                    feature_lookup._default_values = None
            # As server only supports FeatureSpec generation on UC tables. Feature Store client will continue to generate feature spec locally.
            feature_spec = training_scoring_utils.build_feature_spec(
                feature_lookups,
                ft_metadata,
                column_infos,
                exclude_columns,
                self._catalog_client.feature_store_workspace_id,
            )

        return self.create_training_set(
            feature_spec,
            column_infos.feature_column_infos,
            label_names,
            req_context,
            df,
            ft_metadata,
            kwargs=kwargs,
        )

    def create_training_set_from_feature_spec(
        self,
        df: DataFrame,
        feature_spec_name: str,
        label: Union[str, List[str], None],
        exclude_columns: List[str],
        client_name: str,
        **kwargs,
    ) -> TrainingSet:
        req_context = RequestContext(request_context.CREATE_TRAINING_SET, client_name)

        # Initialize label_names with empty list if label is not provided
        label_names = utils.as_list(label, [])
        del label

        training_scoring_utils.verify_df_and_labels(df, label_names, exclude_columns)

        # Get FeatureSpec from UC client.
        function_dict = self._databricks_client.get_uc_function(feature_spec_name)[
            "routine_definition"
        ]
        feature_spec = FeatureSpec._from_dict(yaml.safe_load(function_dict))

        ft_metadata = training_scoring_utils.get_table_metadata(
            self._catalog_client,
            self._catalog_client_helper,
            self._spark_client,
            {table.table_name for table in feature_spec.table_infos},
            req_context,
        )

        source_data_column_infos = [
            ColumnInfo(
                info=SourceDataColumnInfo(col),
                include=True,
                topological_ordering=0,
                data_type=dtype,
            )
            for col, dtype in df.dtypes
            if (col not in label_names) and (col not in exclude_columns)
        ]

        col_info = source_data_column_infos + [
            col
            for col in feature_spec.column_infos
            if (
                not isinstance(col.info, SourceDataColumnInfo)
                and (col.info.output_name not in exclude_columns)
            )
        ]

        col_info = assign_topological_ordering(col_info)

        final_feature_spec = FeatureSpec(
            col_info,
            feature_spec.table_infos,
            feature_spec.function_infos,
            feature_spec.workspace_id,
            feature_spec._feature_store_client_version,
            feature_spec.serialization_version,
        )

        training_scoring_utils.validate_column_infos(
            self._spark_client_helper,
            self._information_schema_spark_client,
            ft_metadata,
            final_feature_spec.source_data_column_infos,
            final_feature_spec.feature_column_infos,
            final_feature_spec.on_demand_column_infos,
            label_names,
        )

        return self.create_training_set(
            final_feature_spec,
            feature_spec.feature_column_infos,
            label_names,
            req_context,
            df,
            ft_metadata,
            kwargs=kwargs,
        )

    def create_training_set_from_features(
        self,
        df: DataFrame,
        features: List[Feature],
        label: Union[str, List[str], None],
        exclude_columns: List[str],
        client_name: str,
        **kwargs,
    ) -> TrainingSetWithDeclarativeFeatures:
        """Create training set directly from Feature objects by computing and joining features.

        This performs point-in-time (as-of) joins between the provided labeled ``df`` and
        the computed feature DataFrames for each underlying Delta table source referenced by ``features``.
        """
        req_context = RequestContext(request_context.CREATE_TRAINING_SET, client_name)

        # Initialize label_names with empty list if label is not provided
        label_names = utils.as_list(label, [])

        training_scoring_utils.verify_df_and_labels(df, label_names, exclude_columns)

        # Only get column infos for the source data columns.
        column_infos = training_scoring_utils.get_column_infos(
            feature_lookups=None,
            feature_functions=None,
            ft_metadata=None,
            df_columns=df.columns,
            label_names=label_names,
        )
        column_infos = [
            ColumnInfo(info=info, include=info.output_name not in exclude_columns)
            for info in column_infos.source_data_column_infos
        ]

        training_scoring_utils.warn_if_non_photon_for_native_spark(
            use_native_spark=True,  # Training set with declarative features always uses native spark join
            spark_client=self._spark_client,
        )

        feature_spec_declarative = FeatureSpecDeclarative(
            column_infos=column_infos,
            features=features,
            workspace_id=self._catalog_client.feature_store_workspace_id,
            feature_store_client_version=VERSION,
            serialization_version=FeatureSpec.SERIALIZATION_VERSION_NUMBER,
        )

        source_dfs = {
            source: source.load_df(self._spark_client)
            for source in {feature.source for feature in features}
        }

        return TrainingSetWithDeclarativeFeatures(
            df=df,
            features=features,
            source_dfs=source_dfs,
            labels=label_names,
            feature_spec=feature_spec_declarative,
        )

    def score_batch(
        self,
        model_uri: Optional[str],
        df: DataFrame,
        result_type: str,
        client_name: str,
        env_manager: Optional[str] = None,
        local_uri: Optional[str] = None,
        params: Optional[dict[str, Any]] = None,
        **kwargs,
    ) -> DataFrame:

        validation_utils.check_dataframe_type(df)
        if (model_uri is None) == (local_uri is None):
            raise ValueError(
                "Either 'model_uri' or 'local_uri' must be provided, but not both."
            )
        if df.isStreaming:
            raise ValueError("Streaming DataFrames are not supported.")

        if PREDICTION_COLUMN_NAME in df.columns:
            raise ValueError(
                "FeatureStoreClient.score_batch returns a DataFrame with a new column "
                f'"{PREDICTION_COLUMN_NAME}". df already has a column with name '
                f'"{PREDICTION_COLUMN_NAME}".'
            )

        utils_common.validate_strings_unique(
            df.columns,
            "The provided DataFrame for scoring must have unique column names. Found duplicates {}.",
        )

        # If the user provided an explicit model_registry_uri when constructing the FeatureStoreClient,
        # we respect this by setting the registry URI prior to reading the model from Model
        # Registry.
        if self._model_registry_uri:
            # This command will override any previously set registry_uri.
            mlflow.set_registry_uri(self._model_registry_uri)

        artifact_path = os.path.join(mlflow.pyfunc.DATA, MODEL_DATA_PATH_ROOT)

        with TempDir() as tmp_location:
            local_path = (
                local_uri
                if local_uri
                else utils.download_model_artifacts(model_uri, tmp_location.path())
            )
            model_data_path = os.path.join(local_path, artifact_path)
            # Augment local workspace metastore tables from 2L to 3L,
            # this will prevent us from erroneously reading data from other catalogs
            loaded_feature_spec = load_feature_spec(model_data_path)
            if isinstance(loaded_feature_spec, FeatureSpecDeclarative):
                feature_spec = loaded_feature_spec
            elif isinstance(loaded_feature_spec, FeatureSpec):
                feature_spec = uc_utils.get_feature_spec_with_full_table_names(
                    loaded_feature_spec
                )
            else:
                raise ValueError(
                    f"Unsupported feature spec type: {type(loaded_feature_spec)}"
                )
            raw_model_path = os.path.join(
                model_data_path, mlflow_model_constants.RAW_MODEL_FOLDER
            )
            predict_udf = self._spark_client.get_predict_udf(
                raw_model_path,
                result_type=result_type,
                env_manager=env_manager,
                params=params,
                prebuilt_env_uri=kwargs.get(_PREBUILT_ENV_URI, None),
            )
            # TODO (ML-17260) Consider reading the timestamp from the backend instead of feature store artifacts
            ml_model = Model.load(
                os.path.join(local_path, mlflow_model_constants.ML_MODEL)
            )
            model_creation_timestamp_ms = (
                utils.utc_timestamp_ms_from_iso_datetime_string(
                    ml_model.utc_time_created
                )
            )

        if isinstance(feature_spec, FeatureSpecDeclarative):
            return self._score_batch_with_feature_spec_declarative(
                feature_spec=feature_spec,
                df=df,
                predict_udf=predict_udf,
            )
        elif isinstance(feature_spec, FeatureSpec):
            req_context = RequestContext(request_context.SCORE_BATCH, client_name)
            return self._score_batch_with_feature_spec_materialized(
                feature_spec=feature_spec,
                df=df,
                req_context=req_context,
                predict_udf=predict_udf,
                model_creation_timestamp_ms=model_creation_timestamp_ms,
                **kwargs,
            )
        else:
            raise ValueError(f"Unsupported feature spec type: {type(feature_spec)}")

    def _score_batch_with_feature_spec_materialized(
        self,
        feature_spec: FeatureSpec,
        df: DataFrame,
        req_context,
        predict_udf,
        model_creation_timestamp_ms: int,
        **kwargs,
    ) -> DataFrame:
        """
        Score a DataFrame using a materialized FeatureSpec.

        Args:
            feature_spec: The FeatureSpec containing feature definitions
            df: Input DataFrame to score
            req_context: Request context for API calls
            predict_udf: Prediction UDF to apply
            model_creation_timestamp_ms: Model creation timestamp in milliseconds
            **kwargs: Additional arguments including USE_SPARK_NATIVE_JOIN

        Returns:
            DataFrame with predictions added
        """
        feature_input_keys = []
        for fci in feature_spec.feature_column_infos:
            feature_input_keys.extend([k for k in fci.lookup_key])
        on_demand_input_names = utils_common.get_unique_list_order(
            [
                input_name
                for odci in feature_spec.on_demand_column_infos
                for input_name in odci.input_bindings.values()
            ]
        )
        intermediate_inputs = set(feature_input_keys + on_demand_input_names)

        source_data_names = [
            sdci.name for sdci in feature_spec.source_data_column_infos
        ]
        feature_output_names = [
            fci.output_name for fci in feature_spec.feature_column_infos
        ]
        on_demand_output_names = [
            odci.output_name for odci in feature_spec.on_demand_column_infos
        ]
        all_output_names = set(
            source_data_names + feature_output_names + on_demand_output_names
        )

        required_cols = intermediate_inputs.difference(all_output_names)
        required_cols.update(source_data_names)

        missing_required_columns = [
            col for col in required_cols if col not in df.columns
        ]
        if missing_required_columns:
            missing_columns_formatted = ", ".join(
                [f"'{s}'" for s in missing_required_columns]
            )
            raise ValueError(
                f"DataFrame is missing required columns {missing_columns_formatted}."
            )

        table_names = {fci.table_name for fci in feature_spec.feature_column_infos}
        feature_table_features_map = training_scoring_utils.get_features_for_tables(
            self._catalog_client, req_context, table_names=table_names
        )
        feature_table_metadata_map = (
            training_scoring_utils.get_feature_table_metadata_for_tables(
                self._catalog_client,
                self._catalog_client_helper,
                req_context,
                table_names=table_names,
            )
        )
        feature_table_data_map = training_scoring_utils.load_feature_data_for_tables(
            self._spark_client, table_names=table_names
        )

        training_scoring_utils.validate_feature_column_infos_data(
            self._spark_client_helper,
            feature_spec.feature_column_infos,
            feature_table_features_map,
            feature_table_data_map,
        )

        # Check if the fetched feature tables match the feature tables logged in training
        self._warn_if_tables_mismatched_for_model(
            feature_spec=feature_spec,
            feature_table_metadata_map=feature_table_metadata_map,
            model_creation_timestamp_ms=model_creation_timestamp_ms,
        )

        uc_function_infos = training_scoring_utils.get_uc_function_infos(
            self._information_schema_spark_client,
            {odci.udf_name for odci in feature_spec.on_demand_column_infos},
        )

        # Required source data and feature lookup keys have been validated to exist in `df`.
        # No additional validation is required before resolving FeatureLookups and applying FeatureFunctions.
        training_scoring_utils.warn_if_non_photon_for_native_spark(
            kwargs.get(_USE_SPARK_NATIVE_JOIN, False), self._spark_client
        )

        augmented_df = TrainingSet(
            feature_spec=feature_spec,
            df=df,
            labels=[],
            feature_table_metadata_map=feature_table_metadata_map,
            feature_table_data_map=feature_table_data_map,
            uc_function_infos=uc_function_infos,
            use_spark_native_join=kwargs.get(_USE_SPARK_NATIVE_JOIN, False),
        )._augment_df()

        # Only included FeatureSpec columns should be part of UDF inputs for scoring.
        # Note: extra `df` columns not in FeatureSpec should be preserved.
        udf_input_columns = [
            ci.output_name for ci in feature_spec.column_infos if ci.include
        ]

        # Apply predictions.
        df_with_predictions = augmented_df.withColumn(
            PREDICTION_COLUMN_NAME, predict_udf(struct(*udf_input_columns))
        )

        # Reorder `df_with_predictions` to include:
        # 1. Preserved `df` columns, in `df` column order.
        # 2. Computed model input columns, in `FeatureSpec` column order.
        # 3. Prediction column.
        output_column_order = (
            df.columns
            + [col for col in udf_input_columns if col not in df.columns]
            + [PREDICTION_COLUMN_NAME]
        )
        return_df = df_with_predictions.select(output_column_order)

        # Add consumer of each feature and track the number of overridden features as final step
        consumer_feature_table_map = defaultdict(list)
        for feature in feature_spec.feature_column_infos:
            consumer_feature_table_map[feature.table_name].append(feature.feature_name)

        # Note: Excluded FeatureColumnInfos should not be counted in the number of overridden FeatureLookups.
        materialized_fcis = [
            ci.info
            for ci in feature_spec.column_infos
            if isinstance(ci.info, FeatureColumnInfo) and ci.include
        ]
        overridden_materialized_fcis = [
            fci for fci in materialized_fcis if fci.output_name in df.columns
        ]

        # Compute number of on-demand inputs, and on-demand outputs that are overridden.
        all_fci_output_names = {
            fci.output_name for fci in feature_spec.feature_column_infos
        }
        overridden_odci_inputs = []
        overridden_odcis = []
        for odci in feature_spec.on_demand_column_infos:
            if odci.output_name in df.columns:
                overridden_odcis.append(odci)
            for odci_input in odci.input_bindings.values():
                if odci_input in all_fci_output_names and odci_input in df.columns:
                    overridden_odci_inputs.append(odci_input)

        additional_add_consumer_headers = {
            request_context.NUM_FEATURES_OVERRIDDEN: str(
                len(overridden_materialized_fcis)
            ),
            request_context.NUM_ON_DEMAND_FEATURES_OVERRIDDEN: str(
                len(overridden_odcis)
            ),
            request_context.NUM_ON_DEMAND_FEATURE_INPUTS_OVERRIDDEN: str(
                len(overridden_odci_inputs)
            ),
        }
        add_consumer_req_context = RequestContext.with_additional_custom_headers(
            req_context, additional_add_consumer_headers
        )

        self._catalog_client_helper.add_consumer(
            consumer_feature_table_map, add_consumer_req_context
        )

        return return_df

    def _score_batch_with_feature_spec_declarative(
        self,
        feature_spec: FeatureSpecDeclarative,
        df: DataFrame,
        predict_udf,
    ) -> DataFrame:
        """
        Score a DataFrame using a FeatureSpecDeclarative.
        """
        if self._materialization_client is None:
            raise ValueError(
                "score_batch with declarative features is not supported, please use FeatureEngineeringClient instead."
            )

        source_dfs = {
            source: source.load_df(self._spark_client)
            for source in {feature.source for feature in feature_spec.features}
        }

        augmented_df = TrainingSetWithDeclarativeFeatures(
            df=df,
            features=feature_spec.features,
            source_dfs=source_dfs,
            labels=[],
            feature_spec=feature_spec,
        )._augment_df()

        # Apply predictions.
        predict_input_columns = [
            column_info.info.name
            for column_info in feature_spec.column_infos
            if column_info.include
        ] + [feature.name for feature in feature_spec.features]
        df_with_predictions = augmented_df.withColumn(
            PREDICTION_COLUMN_NAME, predict_udf(struct(*predict_input_columns))
        )

        return df_with_predictions

    def log_model(
        self,
        model: Any,
        artifact_path: str,
        *,
        flavor: ModuleType,
        training_set: Optional[TrainingSet],
        registered_model_name: Optional[str],
        await_registration_for: int,
        infer_input_example: bool,
        **kwargs,
    ):
        # Validate only one of the training_set, feature_spec_path arguments is provided.
        # Retrieve the FeatureSpec, then remove training_set, feature_spec_path from local scope.
        feature_spec_path = kwargs.pop("feature_spec_path", None)
        if (training_set is None) == (feature_spec_path is None):
            raise ValueError(
                "Either 'training_set' or 'feature_spec_path' must be provided, but not both."
            )
        # Retrieve the FeatureSpec and then reformat tables in local metastore to 2L before serialization.
        # This will make sure the format of the feature spec with local metastore tables is always consistent.
        if training_set:
            if not isinstance(training_set, TrainingSetWithDeclarativeFeatures):
                # Regular TrainingSet flow
                all_tables_in_uc = all(
                    [
                        uc_utils.is_uc_entity(table_info.table_name)
                        for table_info in training_set.feature_spec.table_infos
                    ]
                )
                # training_set.feature_spec is guaranteed to be 3L from FeatureStoreClient.create_training_set.
                feature_spec = uc_utils.get_feature_spec_with_reformat_full_table_names(
                    training_set.feature_spec
                )
            else:
                # For declarative features, create a FeatureSpecDeclarative
                all_tables_in_uc = all(
                    [
                        uc_utils.is_uc_entity(feature.source.full_name())
                        for feature in training_set.features
                    ]
                )
                # Create FeatureSpecDeclarative from the features
                feature_spec = training_set.feature_spec

            label_type_map = training_set._label_data_types
            labels = training_set._labels
            df_head = training_set._df.drop(*labels).head()
        else:
            # FeatureSpec.load expects the root directory of feature_spec.yaml
            root_dir, file_name = os.path.split(feature_spec_path)
            if file_name != FeatureSpec.FEATURE_ARTIFACT_FILE:
                raise ValueError(
                    f"'feature_spec_path' must be a path to {FeatureSpec.FEATURE_ARTIFACT_FILE}."
                )
            feature_spec = FeatureSpec.load(root_dir)

            # The loaded FeatureSpec is not guaranteed to be 3L.
            # First call get_feature_spec_with_full_table_names to append the default metastore to 2L names,
            # as get_feature_spec_with_reformat_full_table_names expects full 3L table names and throws otherwise.
            # TODO (ML-26593): Consolidate this into a single function that allows either 2L/3L names.
            feature_spec_with_full_table_names = (
                uc_utils.get_feature_spec_with_full_table_names(feature_spec)
            )
            all_tables_in_uc = all(
                [
                    uc_utils.is_uc_entity(table_info.table_name)
                    for table_info in feature_spec_with_full_table_names.table_infos
                ]
            )
            feature_spec = uc_utils.get_feature_spec_with_reformat_full_table_names(
                feature_spec_with_full_table_names
            )
            label_type_map = None
            df_head = None
        del training_set, feature_spec_path

        override_output_schema = kwargs.pop("output_schema", None)
        params = kwargs.pop("params", {})
        params["result_type"] = params.get("result_type", _NO_RESULT_TYPE_PASSED)
        # Signatures will ony be supported for UC-table-only models to
        # mitigate new online scoring behavior from being a breaking regression for older
        # models.
        # See https://docs.google.com/document/d/1L5tLY-kRreRefDfuAM3crXvYlirkcPuUUppU8uIMVM0/edit#
        try:
            if all_tables_in_uc:
                signature = get_mlflow_signature_from_feature_spec(
                    feature_spec, label_type_map, override_output_schema, params
                )
            else:
                _logger.warning(
                    "Model could not be logged with a signature because the training set uses feature tables in "
                    "Hive Metastore. Migrate the feature tables to Unity Catalog for model to be logged "
                    "with a signature. "
                    "See https://docs.databricks.com/en/machine-learning/feature-store/uc/upgrade-feature-table-to-uc.html for more details."
                )
                signature = None
        except Exception as e:
            _logger.warning(f"Model could not be logged with a signature: {e}")
            signature = None

        with TempDir() as tmp_location:
            data_path = os.path.join(tmp_location.path(), "feature_store")
            raw_mlflow_model = Model(
                signature=drop_signature_inputs_and_invalid_params(signature)
            )
            raw_model_path = os.path.join(
                data_path, mlflow_model_constants.RAW_MODEL_FOLDER
            )
            if flavor.FLAVOR_NAME != mlflow.pyfunc.FLAVOR_NAME:
                flavor.save_model(
                    model, raw_model_path, mlflow_model=raw_mlflow_model, **kwargs
                )
            else:
                flavor.save_model(
                    raw_model_path,
                    mlflow_model=raw_mlflow_model,
                    python_model=model,
                    **kwargs,
                )
            if not "python_function" in raw_mlflow_model.flavors:
                raise ValueError(
                    f"FeatureStoreClient.log_model does not support '{flavor.__name__}' "
                    f"since it does not have a python_function model flavor."
                )

            # Re-use the conda environment from the raw model for the packaged model. Later, we may
            # add an additional requirement for the Feature Store library. At the moment, however,
            # the databricks-feature-store package is not available via conda or pip.
            model_env = raw_mlflow_model.flavors["python_function"][mlflow.pyfunc.ENV]
            if isinstance(model_env, dict):
                # mlflow 2.0 has multiple supported environments
                conda_file = model_env[mlflow.pyfunc.EnvType.CONDA]
            else:
                conda_file = model_env

            conda_env = read_yaml(raw_model_path, conda_file)

            # Check if databricks-feature-lookup version is specified in conda_env
            lookup_client_version_specified = False
            for dependency in conda_env.get("dependencies", []):
                if isinstance(dependency, dict):
                    for pip_dep in dependency.get("pip", []):
                        if pip_dep.startswith(
                            mlflow_model_constants.FEATURE_LOOKUP_CLIENT_PIP_PACKAGE
                        ):
                            lookup_client_version_specified = True
                            break

            # If databricks-feature-lookup version is not specified, add default version
            if not lookup_client_version_specified:
                # Get the pip package string for the databricks-feature-lookup client
                default_databricks_feature_lookup_pip_package = utils.pip_depependency_pinned_major_version(
                    pip_package_name=mlflow_model_constants.FEATURE_LOOKUP_CLIENT_PIP_PACKAGE,
                    major_version=mlflow_model_constants.FEATURE_LOOKUP_CLIENT_MAJOR_VERSION,
                )
                utils.add_mlflow_pip_depependency(
                    conda_env, default_databricks_feature_lookup_pip_package
                )

            try:
                if (
                    df_head is not None
                    and signature is not None
                    and infer_input_example
                ):
                    input_example = input_example_utils.infer_input_example(
                        df_head, signature
                    )
                else:
                    input_example = None
            except Exception:
                input_example = None

            feature_spec.save(data_path)

            if (
                mlflow.tracking.fluent.active_run() is None
                and not mlflow_log_model_starts_run()
            ):
                mlflow.start_run()
            compatible_parameters = {}
            if is_log_model_artifact_path_deprecated():
                compatible_parameters["name"] = artifact_path
            else:
                compatible_parameters["artifact_path"] = artifact_path
            mlflow.pyfunc.log_model(
                loader_module=mlflow_model_constants.MLFLOW_MODEL_NAME,
                data_path=data_path,
                conda_env=conda_env,
                signature=signature,
                input_example=input_example,
                **compatible_parameters,
            )
        if registered_model_name is not None:
            # The call to mlflow.pyfunc.log_model will create an active run, so it is safe to
            # obtain the run_id for the active run.
            run_id = mlflow.tracking.fluent.active_run().info.run_id

            # If the user provided an explicit model_registry_uri when constructing the FeatureStoreClient,
            # we respect this by setting the registry URI prior to reading the model from Model
            # Registry.
            if self._model_registry_uri:
                # This command will override any previously set registry_uri.
                mlflow.set_registry_uri(self._model_registry_uri)

            mlflow.register_model(
                "runs:/%s/%s" % (run_id, artifact_path),
                registered_model_name,
                await_registration_for=await_registration_for,
            )

    def _warn_if_tables_mismatched_for_model(
        self,
        feature_spec: FeatureSpec,
        feature_table_metadata_map: Dict[str, FeatureTable],
        model_creation_timestamp_ms: float,
    ):
        """
        Helper method to warn if feature tables were deleted and recreated after a model was logged.
        For newer FeatureSpec versions >=3, we can compare the FeatureSpec and current table ids.
        Otherwise, we compare the model and table creation timestamps.
        """
        # 1. Compare feature table ids
        # Check for feature_spec logged with client versions that supports table_infos
        if len(feature_spec.table_infos) > 0:
            # When feature_spec.yaml is parsed, FeatureSpec.load will assert
            # that the listed table names in input_tables match table names in input_columns.
            # The following code assumes this as invariant and only checks for the table IDs.
            mismatched_tables = []
            for table_info in feature_spec.table_infos:
                feature_table = feature_table_metadata_map[table_info.table_name]
                if feature_table and table_info.table_id != feature_table.table_id:
                    mismatched_tables.append(table_info.table_name)
            if len(mismatched_tables) > 0:
                plural = len(mismatched_tables) > 1
                _logger.warning(
                    f"Feature table{'s' if plural else ''} {', '.join(mismatched_tables)} "
                    f"{'were' if plural else 'was'} deleted and recreated after "
                    f"the model was trained. Model performance may be affected if the features "
                    f"used in scoring have drifted from the features used in training."
                )

        # 2. Compare model creation timestamp with feature table creation timestamps
        feature_tables_created_after_model = []
        for name, metadata in feature_table_metadata_map.items():
            if model_creation_timestamp_ms < metadata.creation_timestamp:
                feature_tables_created_after_model.append(name)
        if len(feature_tables_created_after_model) > 0:
            plural = len(feature_tables_created_after_model) > 1
            message = (
                f"Feature table{'s' if plural else ''} {', '.join(feature_tables_created_after_model)} "
                f"{'were' if plural else 'was'} created after the model was logged. "
                f"Model performance may be affected if the features used in scoring have drifted "
                f"from the features used in training."
            )
            _logger.warning(message)

    def create_feature_spec(
        self,
        name: str,
        features: List[Union[FeatureLookup, FeatureFunction]],
        client_name: str,
        exclude_columns: List[str] = [],
    ) -> FeatureSpec:
        req_context = RequestContext(request_context.CREATE_FEATURE_SPEC, client_name)

        feature_lookups = [f for f in features if isinstance(f, FeatureLookup)]
        feature_functions = [f for f in features if isinstance(f, FeatureFunction)]

        # Maximum of 100 FeatureFunctions is supported
        if len(feature_functions) > training_scoring_utils.MAX_FEATURE_FUNCTIONS:
            raise ValueError(
                f"A maximum of {training_scoring_utils.MAX_FEATURE_FUNCTIONS} FeatureFunctions are supported."
            )

        # Get feature table metadata and column infos
        ft_metadata = training_scoring_utils.get_table_metadata(
            self._catalog_client,
            self._catalog_client_helper,
            self._spark_client,
            {fl.table_name for fl in feature_lookups},
            req_context,
        )
        column_infos = training_scoring_utils.get_column_infos(
            feature_lookups,
            feature_functions,
            ft_metadata,
        )

        column_infos = training_scoring_utils.add_inferred_source_columns(column_infos)

        training_scoring_utils.validate_column_infos(
            self._spark_client_helper,
            self._information_schema_spark_client,
            ft_metadata,
            column_infos.source_data_column_infos,
            column_infos.feature_column_infos,
            column_infos.on_demand_column_infos,
        )

        feature_spec = training_scoring_utils.build_feature_spec(
            feature_lookups,
            ft_metadata,
            column_infos,
            exclude_columns,
            self._catalog_client.feature_store_workspace_id,
        )

        # Serialize feature spec into YAML string
        feature_spec_yaml = convert_to_yaml_string(feature_spec)

        additional_headers = {
            request_context.NUM_FUNCTIONS: str(
                len(feature_spec.on_demand_column_infos)
            ),
            request_context.NUM_FEATURES: str(len(feature_spec.feature_column_infos)),
            request_context.NUM_FEATURE_TABLES: str(len(feature_spec.table_infos)),
        }

        # A graph map representing the graph of column infos in the feature spec.
        # Keys are the encoded columns and values are lists of dependencies.
        if len(feature_spec.column_infos) < FEATURE_SPEC_GRAPH_MAX_COLUMN_INFO:
            additional_headers[request_context.FEATURE_SPEC_GRAPH_MAP] = json.dumps(
                get_encoded_graph_map(feature_spec.column_infos)
            )

        feature_spec_info = self._catalog_client.create_feature_spec(
            name,
            feature_spec_yaml,
            features,
            exclude_columns,
            RequestContext.with_additional_custom_headers(
                req_context, additional_headers
            ),
        )
        return feature_spec_info
