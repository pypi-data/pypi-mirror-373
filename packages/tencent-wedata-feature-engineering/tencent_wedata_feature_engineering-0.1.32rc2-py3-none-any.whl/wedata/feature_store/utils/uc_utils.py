import copy
import re
from typing import Optional, Set, Any, List
from datetime import datetime, timezone

from wedata.feature_store.entities.feature_spec import FeatureSpec

SINGLE_LEVEL_NAMESPACE_REGEX = r"^[^\. \/\x00-\x1F\x7F]+$"
TWO_LEVEL_NAMESPACE_REGEX = r"^[^\. \/\x00-\x1F\x7F]+(\.[^\. \/\x00-\x1F\x7F]+)$"
THREE_LEVEL_NAMESPACE_REGEX = (
    r"^[^\. \/\x00-\x1F\x7F]+(\.[^\. \/\x00-\x1F\x7F]+)(\.[^\. \/\x00-\x1F\x7F]+)$"
)

HIVE_METASTORE_NAME = "hive_metastore"
# these two catalog names both points to the workspace local default HMS (hive metastore).
LOCAL_METASTORE_NAMES = [HIVE_METASTORE_NAME,"spark_catalog"]


# Get full table name in the form of <catalog_name>.<schema_name>.<table_name>
# given user specified table name, current catalog and schema.
def get_full_table_name(
    table_name: str,
    current_catalog: str,
    current_schema: str,
) -> str:
    _check_qualified_table_names({table_name})
    return _get_full_name_for_entity(
        name=table_name,
        current_catalog=current_catalog,
        current_schema=current_schema,
        entity_type="table",
    )


# Get full UDF name in the form of <catalog_name>.<schema_name>.<udf_name>
# given user specified UDF name, current catalog and schema.
def get_full_udf_name(
    udf_name: str,
    current_catalog: str,
    current_schema: str,
) -> str:
    _check_qualified_udf_names({udf_name})
    return _get_full_name_for_entity(
        name=udf_name,
        current_catalog=current_catalog,
        current_schema=current_schema,
        entity_type="UDF",
    )


def _get_full_name_for_entity(
    name: str,
    current_catalog: str,
    current_schema: str,
    entity_type: str,
) -> str:
    if not _is_single_level_name(current_catalog) or not _is_single_level_name(
        current_schema
    ):
        raise ValueError(
            f"Invalid catalog '{current_catalog}' or "
            f"schema '{current_schema}' name for {entity_type} '{name}'."
        )
    if _is_single_level_name(name):
        full_name = f"{current_catalog}.{current_schema}.{name}"
    elif _is_two_level_name(name):
        full_name = f"{current_catalog}.{name}"
    elif _is_three_level_name(name):
        full_name = name
    else:
        raise _invalid_names_error({name}, entity_type)

    catalog, schema, name = full_name.split(".")
    if catalog in LOCAL_METASTORE_NAMES:
        return f"{HIVE_METASTORE_NAME}.{schema}.{name}"
    return full_name


def _replace_catalog_name(full_name: str, catalog: Optional[str]) -> str:
    if catalog is None:
        return full_name
    name_sec = full_name.split(".")
    name_sec[0] = catalog
    return ".".join(name_sec)


# Local metastore tables in feature_spec.yaml are all stored in 2L.
# Standardize table names to be all in 3L to avoid erroneously reading data from UC tables.
def get_feature_spec_with_full_table_names(
    feature_spec: FeatureSpec, catalog_name_override: Optional[str] = None
) -> FeatureSpec:
    column_info_table_names = [
        column_info.table_name for column_info in feature_spec.feature_column_infos
    ]
    table_info_table_names = [
        table_info.table_name for table_info in feature_spec.table_infos
    ]
    _check_qualified_table_names(set(column_info_table_names))
    _check_qualified_table_names(set(table_info_table_names))
    invalid_table_names = list(
        filter(_is_single_level_name, column_info_table_names)
    ) + list(filter(_is_single_level_name, table_info_table_names))
    if len(invalid_table_names) > 0:
        raise _invalid_names_error(set(invalid_table_names), "table")
    standardized_feature_spec = copy.deepcopy(feature_spec)
    for column_info in standardized_feature_spec.feature_column_infos:
        if _is_two_level_name(column_info.table_name):
            column_info._table_name = f"{HIVE_METASTORE_NAME}.{column_info.table_name}"
        column_info._table_name = _replace_catalog_name(
            column_info.table_name, catalog_name_override
        )
    for column_info in standardized_feature_spec.on_demand_column_infos:
        if _is_two_level_name(column_info.udf_name):
            column_info._udf_name = f"{HIVE_METASTORE_NAME}.{column_info.udf_name}"
        column_info._udf_name = _replace_catalog_name(
            column_info.udf_name, catalog_name_override
        )
    for table_info in standardized_feature_spec.table_infos:
        if _is_two_level_name(table_info.table_name):
            table_info._table_name = f"{HIVE_METASTORE_NAME}.{table_info.table_name}"
        table_info._table_name = _replace_catalog_name(
            table_info.table_name, catalog_name_override
        )
    for udf_info in standardized_feature_spec.function_infos:
        udf_info._udf_name = _replace_catalog_name(
            udf_info.udf_name, catalog_name_override
        )
    return standardized_feature_spec


# Reformat 3L table name for tables in local metastore to 2L. This is used when interacting with catalog client
# and serializing workspace local feature spec for scoring.
def reformat_full_table_name(full_table_name: str) -> str:
    if not _is_three_level_name(full_table_name):
        raise _invalid_names_error({full_table_name}, "table")
    catalog, schema, table = full_table_name.split(".")
    if catalog in LOCAL_METASTORE_NAMES:
        return f"{schema}.{table}"
    return full_table_name


# Reformat table names in feature_spec with reformat_full_table_name
def get_feature_spec_with_reformat_full_table_names(
    feature_spec: FeatureSpec,
) -> FeatureSpec:
    column_info_table_names = [
        column_info.table_name for column_info in feature_spec.feature_column_infos
    ]
    table_info_table_names = [
        table_info.table_name for table_info in feature_spec.table_infos
    ]
    _check_qualified_table_names(set(column_info_table_names))
    _check_qualified_table_names(set(table_info_table_names))
    invalid_table_names = list(
        filter(lambda name: not _is_three_level_name(name), column_info_table_names)
    ) + list(
        filter(lambda name: not _is_three_level_name(name), table_info_table_names)
    )
    if len(invalid_table_names) > 0:
        raise _invalid_names_error(set(invalid_table_names), "table")
    standardized_feature_spec = copy.deepcopy(feature_spec)
    for column_info in standardized_feature_spec.feature_column_infos:
        column_info._table_name = reformat_full_table_name(column_info.table_name)
    for table_info in standardized_feature_spec.table_infos:
        table_info._table_name = reformat_full_table_name(table_info.table_name)
    return standardized_feature_spec


def _invalid_names_error(invalid_names: Set[str], entity_type: str) -> ValueError:
    return ValueError(
        f"Invalid {entity_type} name{'s' if len(invalid_names) > 1 else ''} '{', '.join(invalid_names)}'."
    )


def _is_qualified_entity_name(name) -> bool:
    return isinstance(name, str) and (
        _is_single_level_name(name)
        or _is_two_level_name(name)
        or _is_three_level_name(name)
    )


def _is_single_level_name(name) -> bool:
    return (
        isinstance(name, str)
        and re.match(SINGLE_LEVEL_NAMESPACE_REGEX, name) is not None
    )


def _is_two_level_name(name) -> bool:
    return (
        isinstance(name, str) and re.match(TWO_LEVEL_NAMESPACE_REGEX, name) is not None
    )


def _is_three_level_name(name) -> bool:
    return (
        isinstance(name, str)
        and re.match(THREE_LEVEL_NAMESPACE_REGEX, name) is not None
    )


def unsupported_api_error_uc(api_name):
    return ValueError(f"{api_name} is not supported for Unity Catalog tables.")


# check if entity is in UC
def is_uc_entity(full_entity_name) -> bool:
    catalog_name, schema_name, table_name = full_entity_name.split(".")
    return not is_default_hms_table(full_entity_name)


def is_default_hms_table(full_table_name) -> bool:
    catalog_name, schema_name, table_name = full_table_name.split(".")
    return catalog_name in LOCAL_METASTORE_NAMES
    # return True


# check if UDF names are in the correct format - 1L, 2L or 3L
def _check_qualified_udf_names(udf_names: Set[str]):
    unqualified_udf_names = [
        udf_name for udf_name in udf_names if not _is_qualified_entity_name(udf_name)
    ]
    if len(unqualified_udf_names) > 0:
        raise ValueError(
            f"UDF name{'s' if len(unqualified_udf_names) > 1 else ''} "
            f"'{', '.join(map(str, unqualified_udf_names))}' must have the form "
            f"<catalog_name>.<schema_name>.<udf_name>, <schema_name>.<udf_name>, "
            f"or <udf_name> and cannot include space or forward-slash."
        )


# check if table names are in the correct format - 1L, 2L or 3L
def _check_qualified_table_names(feature_table_names: Set[str]):
    unqualified_table_names = list(
        filter(
            lambda table_name: not _is_qualified_entity_name(table_name),
            feature_table_names,
        )
    )
    if len(unqualified_table_names) > 0:
        raise ValueError(
            f"Feature table name{'s' if len(unqualified_table_names) > 1 else ''} "
            f"'{', '.join(map(str, unqualified_table_names))}' must have the form "
            f"<catalog_name>.<schema_name>.<table_name>, <database_name>.<table_name>, "
            f"or <table_name> and cannot include space or forward-slash."
        )


# For APIs like create_training_set and score_batch, all tables must all be in
# UC catalog (shareable cross-workspaces) or default HMS (intended to only be used in the current workspace)
# check if all tables are either in UC or default HMS.
def _verify_all_tables_are_either_in_uc_or_in_hms(
    table_names: Set[str], current_catalog: str, current_schema: str
):
    full_table_names = [
        get_full_table_name(table_name, current_catalog, current_schema)
        for table_name in table_names
    ]
    is_valid = all(
        [is_uc_entity(full_table_name) for full_table_name in full_table_names]
    ) or all(
        [is_default_hms_table(full_table_name) for full_table_name in full_table_names]
    )
    if not is_valid:
        raise ValueError(
            f"Feature table names '{', '.join(table_names)}' "
            f"must all be in UC or the local default hive metastore. "
            f"Mixing feature tables from two different storage locations is not allowed."
        )


# For APIs like create_training_set with FeatureFunctions, only UC UDFs are supported.
def _verify_all_udfs_in_uc(
    udf_names: Set[str], current_catalog: str, current_schema: str
):
    full_udf_names = [
        get_full_udf_name(udf_name, current_catalog, current_schema)
        for udf_name in udf_names
    ]
    is_valid = all([is_uc_entity(full_udf_name) for full_udf_name in full_udf_names])
    if not is_valid:
        raise ValueError(f"UDFs must all be in Unity Catalog.")

def utc_timestamp_ms_from_iso_datetime_string(date_string: str) -> int:
    # Python uses seconds for its time granularity, so we multiply by 1000 to convert to milliseconds.
    # The Feature Store backend returns timestamps in milliseconds, so this allows for direct comparisons.
    dt = datetime.fromisoformat(date_string)
    utc_dt = dt.replace(tzinfo=timezone.utc)
    return 1000 * utc_dt.timestamp()

def get_unique_list_order(elements: List[Any]) -> List[Any]:
    """
    Returns unique elements in the order they first appear.
    """
    return list(dict.fromkeys(elements))
