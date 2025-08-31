from typing import Dict, List, Optional

import numpy as np
from pyspark.sql import DataFrame

from databricks.ml_features._information_schema_spark_client._information_schema_spark_client import (
    FunctionInfo,
)
from databricks.ml_features.entities.data_source import DataSource
from databricks.ml_features.entities.data_type import DataType
from databricks.ml_features.entities.feature import Feature
from databricks.ml_features.entities.feature_table import FeatureTable
from databricks.ml_features.utils.feature_lookup_utils import (
    augment_training_df_with_computed_features,
    join_feature_data_if_not_overridden,
)
from databricks.ml_features.utils.on_demand_utils import (
    apply_functions_if_not_overridden,
)
from databricks.ml_features.utils.pit_computation_utils import (
    augment_df_with_pit_computed_features,
)
from databricks.ml_features_common.entities.feature_column_info import FeatureColumnInfo
from databricks.ml_features_common.entities.feature_spec import FeatureSpec
from databricks.ml_features_common.entities.feature_spec_declarative import (
    FeatureSpecDeclarative,
)
from databricks.ml_features_common.utils.data_type_utils import (
    deserialize_default_value_to_data_type,
)
from databricks.ml_features_common.utils.feature_spec_utils import (
    COLUMN_INFO_TYPE_FEATURE,
    COLUMN_INFO_TYPE_ON_DEMAND,
    COLUMN_INFO_TYPE_SOURCE,
    get_feature_execution_groups,
)


class TrainingSet:
    """
    .. note::

       Aliases: `!databricks.feature_engineering.training_set.TrainingSet`, `!databricks.feature_store.training_set.TrainingSet`

    Class that defines :obj:`TrainingSet` objects.

    .. note::

       The :class:`TrainingSet` constructor should not be called directly. Instead,
       call :meth:`create_training_set() <databricks.feature_engineering.client.FeatureEngineeringClient.create_training_set>`.
    """

    def __init__(
        self,
        feature_spec: FeatureSpec,
        df: DataFrame,
        labels: List[str],
        feature_table_metadata_map: Dict[str, FeatureTable],
        feature_table_data_map: Dict[str, DataFrame],
        uc_function_infos: Dict[str, FunctionInfo],
        use_spark_native_join: Optional[bool] = False,
    ):
        """Initialize a :obj:`TrainingSet` object."""
        assert isinstance(
            labels, list
        ), f"Expected type `list` for argument `labels`. Got '{labels}' with type '{type(labels)}'."

        self._feature_spec = feature_spec
        self._df = df
        self._labels = labels
        self._feature_table_metadata_map = feature_table_metadata_map
        self._feature_table_data_map = feature_table_data_map
        self._uc_function_infos = uc_function_infos
        self._use_spark_native_join = use_spark_native_join
        self._default_values = {}
        # Resolve label column data types.
        self._label_data_types = {
            name: data_type for name, data_type in df.dtypes if name in labels
        }
        # Perform basic validations.
        if self._feature_spec is not None:
            self._validate_and_inject_dtypes()
            self._calculate_default_values()

    @property
    def feature_spec(self) -> FeatureSpec:
        return self._feature_spec

    def _augment_df(self) -> DataFrame:
        """
        Internal helper to augment DataFrame with feature lookups and on-demand features specified in the FeatureSpec.
        Does not drop excluded columns, and does not overwrite columns that already exist.
        Return column order is df.columns + feature lookups + on-demand features.
        """
        result_df = self._df

        execution_groups = get_feature_execution_groups(
            self.feature_spec, self._df.columns
        )

        # Iterate over all levels and type of DAG nodes in FeatureSpec and execute them.
        for execution_group in execution_groups:
            if execution_group.type == COLUMN_INFO_TYPE_SOURCE:
                continue
            if execution_group.type == COLUMN_INFO_TYPE_FEATURE:
                # Apply FeatureLookups
                result_df = join_feature_data_if_not_overridden(
                    feature_spec=self.feature_spec,
                    df=result_df,
                    features_to_join=execution_group.features,
                    feature_table_metadata_map=self._feature_table_metadata_map,
                    feature_table_data_map=self._feature_table_data_map,
                    use_spark_native_join=self._use_spark_native_join,
                )
            elif execution_group.type == COLUMN_INFO_TYPE_ON_DEMAND:
                # Apply all on-demand UDFs
                result_df = apply_functions_if_not_overridden(
                    df=result_df,
                    functions_to_apply=execution_group.features,
                    uc_function_infos=self._uc_function_infos,
                )
            else:
                # This should never be reached.
                raise Exception("Unknown feature execution type:", execution_group.type)

        if self._default_values:
            result_df = result_df.fillna(value=self._default_values)

        return result_df

    def _validate_and_inject_dtypes(self):
        """
        Performs validations through _augment_df (e.g. Delta table exists, Delta and feature table dtypes match),
        then inject the result DataFrame dtypes into the FeatureSpec.
        """
        augmented_df = self._augment_df()
        augmented_df_dtypes = {column: dtype for column, dtype in augmented_df.dtypes}

        # Inject the result DataFrame column types into the respective ColumnInfo
        for ci in self.feature_spec.column_infos:
            ci._data_type = augmented_df_dtypes[ci.output_name]

    def _calculate_default_values(self):
        """
        Calculate default values for the feature spec.
        """
        for ci in self.feature_spec.column_infos:
            if isinstance(ci.info, FeatureColumnInfo):
                if not ci.info.default_value_str:
                    continue
                try:
                    data_type = DataType.from_spark_simple_name(ci.data_type)
                except Exception:
                    raise ValueError(
                        f"Unknown data type for default value: {ci.data_type}"
                    )

                default_value = deserialize_default_value_to_data_type(
                    ci.info.default_value_str, data_type
                )
                if default_value is not None:
                    self._default_values[ci.output_name] = default_value

    def get_output_columns(self) -> List[str]:
        """
        Get the list of output columns that should be included in the final DataFrame.

        This method determines which columns should be included based on the feature_spec
        configuration. If feature_spec has column_infos, it returns only the columns
        marked for inclusion plus labels. Otherwise, it returns an empty list.

        :return: List of column names to include in the output
        """
        if self.feature_spec and self.feature_spec.column_infos:
            # Return only included columns in order defined by FeatureSpec + labels
            return [
                ci.output_name for ci in self.feature_spec.column_infos if ci.include
            ] + self._labels
        else:
            # Return empty list if no feature_spec or column_infos
            return []

    def load_df(self) -> DataFrame:
        """
        Load a :class:`DataFrame <pyspark.sql.DataFrame>`.

        Return a :class:`DataFrame <pyspark.sql.DataFrame>` for training.

        The returned :class:`DataFrame <pyspark.sql.DataFrame>` has columns specified
        in the ``feature_spec`` and ``labels`` parameters provided
        in :meth:`create_training_set() <databricks.feature_engineering.client.FeatureEngineeringClient.create_training_set>`.

        :return:
           A :class:`DataFrame <pyspark.sql.DataFrame>` for training
        """
        augmented_df = self._augment_df()
        included_columns = self.get_output_columns()
        # If no columns specified, return all columns from augmented_df
        if not included_columns:
            return augmented_df
        return augmented_df.select(included_columns)


class TrainingSetWithDeclarativeFeatures(TrainingSet):
    """
    TrainingSet for declarative features defined using Feature objects.

    This class handles training sets created from Feature objects that define
    computations over DataSource objects, rather than traditional FeatureSpec-based lookups.

    .. note::

       The constructor should not be called directly. Instead, use the
       FeatureEngineeringClient.create_training_set() method with features parameter.
    """

    def __init__(
        self,
        *,  # Force all arguments to be keyword-only
        df: DataFrame,
        labels: List[str],
        features: List[Feature],
        source_dfs: Dict[DataSource, DataFrame],
        feature_spec: FeatureSpecDeclarative,
    ):
        """
        Initialize a TrainingSetWithDeclarativeFeatures object.

        :param df: The base DataFrame containing labels and primary keys
        :param features: List of Feature objects defining the computations
        :param source_dfs: Dictionary mapping DataSource to DataFrame with loaded contents
        :param labels: List of label column names
        :param feature_spec: FeatureSpecDeclarative for the features
        """
        # Store features for potential future use (validation, introspection, etc.)
        self._features = features

        # Store the FeatureSpecDeclarative if provided
        self._feature_spec_declarative = feature_spec

        # Store source DataFrames mapping for our specialized use
        self._source_dfs = source_dfs

        # Minimal validation: verify features and source_dfs are consistent
        self._validate_features_and_source_dfs(features, source_dfs)

        # Call parent constructor with defaults appropriate for declarative features
        super().__init__(
            feature_spec=feature_spec,
            df=df,
            labels=labels,
            feature_table_metadata_map={},  # Not used for declarative features
            feature_table_data_map={},  # Not used for declarative features
            uc_function_infos={},  # Not used for declarative features
            use_spark_native_join=True,  # Always True for declarative features
        )

    @property
    def feature_spec(self) -> FeatureSpecDeclarative:
        return self._feature_spec_declarative

    def _validate_features_and_source_dfs(
        self, features: List[Feature], source_dfs: Dict[DataSource, DataFrame]
    ) -> None:
        """
        Perform minimal validation that features and source_dfs are consistent.

        Args:
            features: List of Feature objects defining the computations
            source_dfs: Dictionary mapping DataSource to DataFrame with loaded contents

        Raises:
            ValueError: If validation fails
        """
        # Verify that all feature.data_source is included in source_dfs keys
        feature_sources = {feature.source for feature in features}
        computed_sources = set(source_dfs.keys())

        missing_sources = feature_sources - computed_sources
        if missing_sources:
            raise ValueError(
                f"Features reference DataSources not found in source_dfs: {missing_sources}"
            )

    def _augment_df(self) -> DataFrame:
        """
        Augment DataFrame with computed features from declarative Feature objects.

        Uses point-in-time computation with microsecond precision to ensure temporal correctness.
        """
        return augment_df_with_pit_computed_features(
            self._df, self._features, self._source_dfs
        )

    @property
    def features(self) -> List[Feature]:
        """Get the list of Feature objects used to create this training set."""
        return self._features

    def get_output_columns(self) -> List[str]:
        """
        Get the list of output columns that should be included in the final DataFrame.

        This override for TrainingSetWithDeclarativeFeatures additionally includes all
        feature names from the Feature objects.

        :return: List of column names to include in the output, including all feature names
        """
        base_columns = super().get_output_columns()
        feature_names = [feature.name for feature in self._features]

        # For declarative features, we always want features + labels
        # If base_columns is empty (no feature_spec), add labels manually
        if not base_columns:
            base_columns = self._labels

        # Start with base columns, then add feature names not already present
        base_columns_set = set(base_columns)
        additional_features = [
            name for name in feature_names if name not in base_columns_set
        ]

        return base_columns + additional_features
