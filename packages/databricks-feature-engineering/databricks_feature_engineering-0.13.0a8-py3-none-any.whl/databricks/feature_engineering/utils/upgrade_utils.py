from typing import Any, Dict, List

from databricks.ml_features.entities.data_type import DataType


# strings containing \ or ' can break sql statements, so escape them.
def escape_sql_string(input_str: str) -> str:
    return input_str.replace("\\", "\\\\").replace("'", "\\'")


def upgrade_msg(property: str, source_table: str, target_table: str):
    msg = f"Upgrading {property} from source table '{source_table}' to target table '{target_table}'..."
    return msg


def target_table_source_table_mismatch_msg(
    property: str,
    source_workspace_table_value: Any,
    target_uc_table_value: Any,
    source_table: str,
    target_table: str,
):
    msg = (
        f"{property} from source table '{source_table}' do not match with target table '{target_table}'. "
        f"Source {property.lower()} = '{source_workspace_table_value}' but target {property.lower()} = "
        f"'{target_uc_table_value}'."
    )
    return msg


def raise_target_table_not_match_source_table_warning(
    property: str,
    source_workspace_table_value,
    target_uc_table_value,
    source_table: str,
    target_table: str,
):
    msg = (
        target_table_source_table_mismatch_msg(
            property,
            source_workspace_table_value,
            target_uc_table_value,
            source_table,
            target_table,
        )
        + f" {property} will not be set on target table. "
        f"To overwrite the existing value, "
        f"call upgrade_workspace_table with the parameter overwrite = True."
    )
    return msg


def raise_target_table_not_match_source_table_error(
    property: str,
    source_workspace_table_value: Any,
    target_uc_table_value: Any,
    source_table: str,
    target_table: str,
):
    msg = (
        target_table_source_table_mismatch_msg(
            property,
            source_workspace_table_value,
            target_uc_table_value,
            source_table,
            target_table,
        )
        + f" To overwrite the existing value, "
        f"call upgrade_workspace_table with the parameter overwrite = True."
    )
    raise RuntimeError(msg)


def raise_source_table_not_match_target_table_schema_error(
    source_table_features, target_table_schema, source_table: str, target_table: str
):
    catalog_schema = {
        feature.name: feature.data_type for feature in source_table_features
    }
    delta_schema = {
        feature.name: DataType.spark_type_to_string(feature.dataType)
        for feature in target_table_schema
    }
    msg = (
        f"The source table '{source_table}' and target table '{target_table}' schemas are not identical. "
        f"Source workspace table schema is '{catalog_schema}' while target Unity Catalog table's schema "
        f"is '{delta_schema}'. Fix the differences and call upgrade_workspace_table again."
    )
    raise RuntimeError(msg)


# Return true if source and target are equal or when source[key] != target[key], target[key] is empty
def compare_column_desc_map(source: Dict[str, str], target: Dict[str, str]) -> bool:
    # Keys must be the same
    if set(source.keys()) != set(target.keys()):
        return False
    for key in source:
        if key in target:
            if source[key] != target[key] and target[key]:
                return False
        else:
            return False

    return True


def format_tags(data_list: List[Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    result_dict = {}
    for item in data_list:
        column_name = item["column_name"]
        tag_name = item["tag_name"]
        tag_value = item["tag_value"]

        if column_name not in result_dict:
            result_dict[column_name] = {}

        result_dict[column_name][tag_name] = tag_value
    return result_dict
