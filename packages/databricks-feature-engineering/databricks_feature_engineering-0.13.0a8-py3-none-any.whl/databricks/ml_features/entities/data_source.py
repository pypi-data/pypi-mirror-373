import abc
from enum import Enum
from typing import Any, Dict, List, Optional

from databricks.ml_features_common.entities._feature_store_object import (
    _FeatureStoreObject,
)


class DataSourceTypes(Enum):
    """Enumeration of supported data source types."""

    DELTA = "delta"
    UNIFORM = "uniform"
    KAFKA = "kafka"
    VOLUME = "volume"
    DATAFRAME = "dataframe"


class DataSource(_FeatureStoreObject, abc.ABC):
    """
    Abstract base class for data sources used in feature computation.

    :param source_type: The type of data source
    :param entity_columns: List of column names that serve as primary keys
    :param timeseries_column: Column name that contains timestamp data
    """

    def __init__(
        self,
        *,
        source_type: DataSourceTypes,
        entity_columns: List[str],
        timeseries_column: str,
    ):
        """Initialize a DataSource object. See class documentation."""
        self._validate_parameters(source_type, entity_columns, timeseries_column)

        self._source_type = source_type
        self._entity_columns = entity_columns
        self._timeseries_column = timeseries_column
        self._order_column = f"___{timeseries_column}_as_long"

    @property
    def source_type(self) -> DataSourceTypes:
        """The type of data source."""
        return self._source_type

    @property
    def entity_columns(self) -> List[str]:
        """List of column names that serve as primary keys."""
        return self._entity_columns

    @property
    def timeseries_column(self) -> str:
        """Column name that contains timestamp data."""
        return self._timeseries_column

    @property
    def order_column(self) -> str:
        """The column name for the order column."""
        return self._order_column

    @abc.abstractmethod
    def full_name(self) -> str:
        """Return the full name/identifier for this data source."""
        raise NotImplementedError()

    @abc.abstractmethod
    def load_df(self, spark_client):
        """Load the data source as a Spark DataFrame. Must be implemented by all derived classes."""
        raise NotImplementedError()

    @abc.abstractmethod
    def __hash__(self):
        """Make DataSource hashable. Must be implemented by all derived classes."""
        raise NotImplementedError()

    def _validate_parameters(
        self,
        source_type: DataSourceTypes,
        entity_columns: List[str],
        timeseries_column: str,
    ):
        """Validates the parameters provided to the DataSource class."""
        if not isinstance(source_type, DataSourceTypes):
            raise ValueError("The 'source_type' must be a DataSourceTypes enum value.")

        if not isinstance(entity_columns, list):
            raise ValueError("The 'entity_columns' must be a list.")

        if not entity_columns:
            raise ValueError(
                "The 'entity_columns' must contain at least one column name."
            )

        for i, column in enumerate(entity_columns):
            if not isinstance(column, str) or not column.strip():
                raise ValueError(
                    f"All entity columns must be non-empty strings. "
                    f"Invalid column at index {i}: {column}"
                )

        if not isinstance(timeseries_column, str) or not timeseries_column.strip():
            raise ValueError("The 'timeseries_column' must be a non-empty string.")

    @classmethod
    def _from_yaml_dict(cls, data_source_dict: Dict[str, Any]) -> "DataSource":
        """Create a DataSource from a dictionary loaded from YAML."""
        if (
            DeltaTableSource.CATALOG_NAME_FIELD_NAME in data_source_dict
            and DeltaTableSource.SCHEMA_NAME_FIELD_NAME in data_source_dict
            and DeltaTableSource.TABLE_NAME_FIELD_NAME in data_source_dict
        ):
            return DeltaTableSource._from_yaml_dict(data_source_dict)
        else:
            raise ValueError(
                f"Unsupported data source type in dictionary: {data_source_dict}"
            )


class DeltaTableSource(DataSource):
    """
    Data source implementation for Delta Lake tables.

    :param catalog_name: The name of the Unity Catalog catalog
    :param schema_name: The name of the schema within the catalog
    :param table_name: The name of the table within the schema
    :param entity_columns: List of column names that serve as primary keys
    :param timeseries_column: Column name that contains timestamp data
    """

    CATALOG_NAME_FIELD_NAME = "catalog"
    SCHEMA_NAME_FIELD_NAME = "schema"
    TABLE_NAME_FIELD_NAME = "table"
    ENTITY_COLUMNS_FIELD_NAME = "entity_columns"
    TIMESERIES_COLUMN_FIELD_NAME = "timeseries_column"

    def __init__(
        self,
        *,
        catalog_name: str,
        schema_name: str,
        table_name: str,
        entity_columns: List[str],
        timeseries_column: str,
    ):
        """Initialize a DeltaTableSource object. See class documentation."""
        self._validate_delta_parameters(catalog_name, schema_name, table_name)

        # Initialize the parent with DELTA type
        super().__init__(
            source_type=DataSourceTypes.DELTA,
            entity_columns=entity_columns,
            timeseries_column=timeseries_column,
        )

        self._catalog_name = catalog_name
        self._schema_name = schema_name
        self._table_name = table_name

    @property
    def catalog_name(self) -> str:
        """The name of the Unity Catalog catalog."""
        return self._catalog_name

    @property
    def schema_name(self) -> str:
        """The name of the schema within the catalog."""
        return self._schema_name

    @property
    def table_name(self) -> str:
        """The name of the table within the schema."""
        return self._table_name

    def full_name(self) -> str:
        """Return the full table name in catalog.schema.table format."""
        return f"{self._catalog_name}.{self._schema_name}.{self._table_name}"

    def load_df(self, spark_client):
        """Load the Delta table as a Spark DataFrame."""
        return spark_client.read_table(self.full_name())

    def __hash__(self):
        """Make DeltaTableSource hashable by using immutable representations of its attributes."""
        # Create a tuple of all the key attributes including Delta-specific ones
        return hash(
            (
                self._source_type,
                tuple(self._entity_columns),
                self._timeseries_column,
                self._catalog_name,
                self._schema_name,
                self._table_name,
            )
        )

    def _validate_delta_parameters(
        self, catalog_name: str, schema_name: str, table_name: str
    ):
        """Validates Delta-specific parameters."""
        if not catalog_name or not isinstance(catalog_name, str):
            raise ValueError("The 'catalog_name' must be a non-empty string.")

        if not schema_name or not isinstance(schema_name, str):
            raise ValueError("The 'schema_name' must be a non-empty string.")

        if not table_name or not isinstance(table_name, str):
            raise ValueError("The 'table_name' must be a non-empty string.")

    def _to_yaml_dict(self) -> Dict[str, Any]:
        """Convert the DeltaTableSource to a dictionary that can be used to generate a YAML file."""
        return {
            DeltaTableSource.CATALOG_NAME_FIELD_NAME: self._catalog_name,
            DeltaTableSource.SCHEMA_NAME_FIELD_NAME: self._schema_name,
            DeltaTableSource.TABLE_NAME_FIELD_NAME: self._table_name,
            DeltaTableSource.ENTITY_COLUMNS_FIELD_NAME: self._entity_columns,
            DeltaTableSource.TIMESERIES_COLUMN_FIELD_NAME: self._timeseries_column,
        }

    @classmethod
    def _from_yaml_dict(cls, data_source_dict: Dict[str, Any]) -> "DeltaTableSource":
        """Create a DeltaTableSource from a dictionary loaded from YAML."""
        return cls(
            catalog_name=data_source_dict[DeltaTableSource.CATALOG_NAME_FIELD_NAME],
            schema_name=data_source_dict[DeltaTableSource.SCHEMA_NAME_FIELD_NAME],
            table_name=data_source_dict[DeltaTableSource.TABLE_NAME_FIELD_NAME],
            entity_columns=data_source_dict[DeltaTableSource.ENTITY_COLUMNS_FIELD_NAME],
            timeseries_column=data_source_dict[
                DeltaTableSource.TIMESERIES_COLUMN_FIELD_NAME
            ],
        )


class VolumeSource(DataSource):
    """
    Data source implementation for Unity Catalog Volumes.

    TODO: Implementation to be defined based on volume requirements.
    """

    def __init__(
        self,
        *,
        entity_columns: List[str],
        timeseries_column: str,
    ):
        """Initialize a VolumeSource object. See class documentation."""
        super().__init__(
            source_type=DataSourceTypes.VOLUME,
            entity_columns=entity_columns,
            timeseries_column=timeseries_column,
        )

    def full_name(self) -> str:
        """Return the full volume path identifier."""
        # TODO: Implement volume-specific naming convention
        raise NotImplementedError("VolumeSource.full_name() is not yet implemented.")

    def load_df(self, spark_client):
        """Load the volume data as a Spark DataFrame."""
        # TODO: Implement volume-specific DataFrame loading
        raise NotImplementedError("VolumeSource.load_df() is not yet implemented.")

    def __hash__(self):
        """Make VolumeSource hashable."""
        # TODO: Implement volume-specific hash when volume attributes are defined
        raise NotImplementedError("VolumeSource.__hash__() is not yet implemented.")


class KafkaSource(DataSource):
    """
    Data source implementation for Kafka streams.

    TODO: Implementation to be defined based on Kafka requirements.
    """

    def __init__(
        self,
        *,
        entity_columns: List[str],
        timeseries_column: str,
    ):
        """Initialize a KafkaSource object. See class documentation."""
        super().__init__(
            source_type=DataSourceTypes.KAFKA,
            entity_columns=entity_columns,
            timeseries_column=timeseries_column,
        )

    def full_name(self) -> str:
        """Return the full Kafka topic identifier."""
        # TODO: Implement Kafka-specific naming convention
        raise NotImplementedError("KafkaSource.full_name() is not yet implemented.")

    def load_df(self, spark_client):
        """Load the Kafka stream as a Spark DataFrame."""
        # TODO: Implement Kafka-specific DataFrame loading
        raise NotImplementedError("KafkaSource.load_df() is not yet implemented.")

    def __hash__(self):
        """Make KafkaSource hashable."""
        # TODO: Implement Kafka-specific hash when Kafka attributes are defined
        raise NotImplementedError("KafkaSource.__hash__() is not yet implemented.")


class DataFrameSource(DataSource):
    """
    Data source implementation for Spark DataFrames.

    This allows using an existing Spark DataFrame directly as a data source
    for feature computation, useful for in-memory data processing and testing.

    :param dataframe: The Spark DataFrame to use as the data source
    :param entity_columns: List of column names that serve as primary keys
    :param timeseries_column: Column name that contains timestamp data
    :param source_name: Optional name for the DataFrame source (for identification)
    """

    def __init__(
        self,
        *,
        dataframe,  # Will be validated as Spark DataFrame
        entity_columns: List[str],
        timeseries_column: str,
        source_name: Optional[str] = None,
    ):
        """Initialize a DataFrameSource object. See class documentation."""
        self._validate_dataframe_parameters(dataframe, source_name)

        # Initialize the parent with DATAFRAME type
        super().__init__(
            source_type=DataSourceTypes.DATAFRAME,
            entity_columns=entity_columns,
            timeseries_column=timeseries_column,
        )

        self._dataframe = dataframe
        self._source_name = source_name

    @property
    def dataframe(self):
        """The Spark DataFrame being used as the data source."""
        return self._dataframe

    @property
    def source_name(self) -> str:
        """The name identifier for this DataFrame source."""
        return self._source_name

    def full_name(self) -> str:
        """Return the source name identifier for this DataFrame."""
        return (
            self._source_name
            if self._source_name
            else f"DataFrameSource with schema : {self.dataframe.schema.simpleString()}"
        )

    def load_df(self, spark_client):
        """Return the existing Spark DataFrame."""
        return self._dataframe

    def __hash__(self):
        """Make DataFrameSource hashable by using immutable representations of its attributes."""
        # Get schema information from the DataFrame
        # Convert schema to a hashable representation (sorted tuple of field names and types)
        # Sort by field name to ensure consistent hashing regardless of field order
        schema_fields = tuple(
            sorted(
                (field.name, str(field.dataType))
                for field in self._dataframe.schema.fields
            )
        )

        # Note: We cannot hash the DataFrame itself as it's mutable
        # Use source_name and schema as the identifier for the DataFrame
        return hash(
            (
                self._source_type,
                tuple(self._entity_columns),
                self._timeseries_column,
                self._source_name,
                schema_fields,
            )
        )

    def _validate_dataframe_parameters(self, dataframe, source_name: str):
        """Validates DataFrame-specific parameters."""
        if dataframe is None:
            raise ValueError("The 'dataframe' cannot be None.")

        # Import DataFrame locally for isinstance check
        try:
            from pyspark.sql import DataFrame

            if not isinstance(dataframe, DataFrame):
                raise ValueError("The 'dataframe' must be a valid Spark DataFrame.")
        except ImportError:
            raise ImportError("PySpark is required to use DataFrameSource.")

        if source_name is not None and (
            not isinstance(source_name, str) or not source_name.strip()
        ):
            raise ValueError(
                "The 'source_name' must be a non-empty string if provided."
            )
