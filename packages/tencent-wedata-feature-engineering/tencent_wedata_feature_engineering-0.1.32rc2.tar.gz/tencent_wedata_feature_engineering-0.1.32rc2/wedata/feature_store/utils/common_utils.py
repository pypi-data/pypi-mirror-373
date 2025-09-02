"""
通用工具函数
"""
import os
import json
from collections import Counter
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import mlflow
from mlflow.exceptions import RestException
from mlflow.store.artifact.artifact_repository_registry import get_artifact_repository
from mlflow.store.artifact.models_artifact_repo import ModelsArtifactRepository
from mlflow.store.artifact.runs_artifact_repo import RunsArtifactRepository
from mlflow.utils import databricks_utils

from wedata.feature_store.constants import constants
from wedata.feature_store.constants.constants import MODEL_DATA_PATH_ROOT

import logging

# 配置日志（可选，根据实际情况配置）
logging.basicConfig(level=logging.ERROR)


def validate_table_name(name: str):
    """
    验证特征表名规范，仅支持单表名，不能包含点（如<catalog>.<schema>.<table>）

    参数:
        name: 要验证的表名

    异常:
        ValueError: 如果表名包含点或不符合规范
    """
    if not name or not isinstance(name, str):
        raise ValueError("Table name must be a non-empty string")
    if name.count('.') > 0:
        raise ValueError("Feature table name only supports single table name, cannot contain dots (e.g. <catalog>.<schema>.<table>)")
    if not name[0].isalpha():
        raise ValueError("Table name must start with a letter")
    if not all(c.isalnum() or c == '_' for c in name):
        raise ValueError("Table name can only contain letters, numbers and underscores")


def build_full_table_name(table_name: str, database_name: Optional[str] = None) -> str:
    """
    构建完整的表名，格式化为`<database>.<table>`形式。

    Args:
        table_name: 输入的表名（可以是简化的表名或完整表名）。
        database_name: 数据库名

    Returns:
        完整表名（`<database>.<table>`）。
    """

    feature_store_database_name = os.environ.get("WEDATA_DEFAULT_FEATURE_STORE_DATABASE")
    if database_name:
        feature_store_database_name = database_name

    if not feature_store_database_name:
        logging.error("The current user has not configured a default feature database. Please contact the manager account to configure it.")
        raise RuntimeError("Feature store is not configured! Please contact the main account to configure it.")

    logging.info("feature database:{}".format(feature_store_database_name))

    feature_store_database = f"{feature_store_database_name}.{table_name}"

    return feature_store_database


def enable_if(condition):
    """
    A decorator that conditionally enables a function based on a condition.
    If the condition is not truthy, calling the function raises a NotImplementedError.

    :param condition: A callable that returns a truthy or falsy value.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not condition():
                raise NotImplementedError
            return func(*args, **kwargs)

        return wrapper

    return decorator


def is_empty(target: str):
    return target is None or len(target.strip()) == 0


class _NoDbutilsError(Exception):
    pass


def _get_dbutils():
    try:
        import IPython

        ip_shell = IPython.get_ipython()
        if ip_shell is None:
            raise _NoDbutilsError
        return ip_shell.ns_table["user_global"]["dbutils"]
    except ImportError:
        raise _NoDbutilsError
    except KeyError:
        raise _NoDbutilsError


def utc_timestamp_ms_from_iso_datetime_string(date_string: str) -> int:
    dt = datetime.fromisoformat(date_string)
    utc_dt = dt.replace(tzinfo=timezone.utc)
    return 1000 * utc_dt.timestamp()


def pip_depependency_pinned_major_version(pip_package_name, major_version):
    """
    Generate a pip dependency string that is pinned to a major version, for example: "databricks-feature-lookup==0.*"
    """
    return f"{pip_package_name}=={major_version}.*"


def add_mlflow_pip_depependency(conda_env, pip_package_name):
    """
    Add a new pip dependency to the conda environment taken from the raw MLflow model.
    """
    if pip_package_name is None or len(pip_package_name) == 0:
        raise ValueError(
            "Unexpected input: missing or empty pip_package_name parameter"
        )

    found_pip_dependency = False
    if conda_env is not None:
        for dep in conda_env["dependencies"]:
            if isinstance(dep, dict) and "pip" in dep:
                found_pip_dependency = True
                pip_deps = dep["pip"]
                if pip_package_name not in pip_deps:
                    pip_deps.append(pip_package_name)
        if "dependencies" in conda_env and not found_pip_dependency:
            raise ValueError(
                "Unexpected input: mlflow conda_env did not contain pip as a dependency"
            )


def download_model_artifacts(model_uri, dir):
    """
    Downloads model artifacts from model_uri to dir.
    """
    if not is_artifact_uri(model_uri):
        raise ValueError(
            f"Invalid model URI '{model_uri}'."
            f"Use ``models:/model_name>/<version_number>`` or "
            f"``runs:/<mlflow_run_id>/run-relative/path/to/model``."
        )

    try:
        repo = get_artifact_repository(model_uri)
    except RestException as e:
        raise ValueError(f"The model at '{model_uri}' does not exist.", e)

    artifact_path = os.path.join("artifacts", MODEL_DATA_PATH_ROOT)
    if len(repo.list_artifacts(artifact_path)) == 0:
        raise ValueError(
            f"No suitable model found at '{model_uri}'. Either no model exists in this "
            f"artifact location or an existing model was not packaged with Feature Store metadata. "
            f"Only models logged by FeatureStoreClient.log_model can be used in inference."
        )

    return repo.download_artifacts(artifact_path="", dst_path=dir)


def validate_params_non_empty(params: Dict[str, Any], expected_params: List[str]):
    """
    Validate that none of the expected parameters are empty.
    """
    for expected_param in expected_params:
        if expected_param not in params:
            raise ValueError(
                f'Internal error: expected parameter "{expected_param}" not found in params dictionary'
            )
        param_value = params[expected_param]
        if not param_value:
            raise ValueError(f'Parameter "{expected_param}" cannot be empty')


def get_workspace_url() -> Optional[str]:
    """
    Overrides the behavior of the mlflow.utils.databricks_utils.get_workspace_url().
    """
    workspace_url = databricks_utils.get_workspace_url()
    if workspace_url and not urlparse(workspace_url).scheme:
        workspace_url = "https://" + workspace_url
    return workspace_url


def is_artifact_uri(uri):
    """
    Checks the artifact URI is associated with a MLflow model or run.
    The actual URI can be a model URI, model URI + subdirectory, or model URI + path to artifact file.
    """
    return ModelsArtifactRepository.is_models_uri(
        uri
    ) or RunsArtifactRepository.is_runs_uri(uri)


def as_list(obj, default=None):
    if not obj:
        return default
    elif isinstance(obj, list):
        return obj
    else:
        return [obj]


def get_duplicates(elements: List[Any]) -> List[Any]:
    """
    Returns duplicate elements in the order they first appear.
    """
    element_counts = Counter(elements)
    duplicates = []
    for e in element_counts.keys():
        if element_counts[e] > 1:
            duplicates.append(e)
    return duplicates


def validate_strings_unique(strings: List[str], error_template: str):
    """
    Validates all strings are unique, otherwise raise ValueError with the error template and duplicates.
    Passes single-quoted, comma delimited duplicates to the error template.
    """
    duplicate_strings = get_duplicates(strings)
    if duplicate_strings:
        duplicates_formatted = ", ".join([f"'{s}'" for s in duplicate_strings])
        raise ValueError(error_template.format(duplicates_formatted))


def sanitize_identifier(identifier: str):
    """
    Sanitize and wrap an identifier with backquotes. For example, "a`b" becomes "`a``b`".
    Use this function to sanitize identifiers such as column names in SQL and PySpark.
    """
    return f"`{identifier.replace('`', '``')}`"


def sanitize_identifiers(identifiers: List[str]):
    """
    Sanitize and wrap the identifiers in a list with backquotes.
    """
    return [sanitize_identifier(i) for i in identifiers]


def sanitize_multi_level_name(multi_level_name: str):
    """
    Sanitize a multi-level name (such as an Unity Catalog table name) by sanitizing each segment
    and joining the results. For example, "ca+t.fo`o.ba$r" becomes "`ca+t`.`fo``o`.`ba$r`".
    """
    segments = multi_level_name.split(".")
    return ".".join(sanitize_identifiers(segments))


def unsanitize_identifier(identifier: str):
    """
    Unsanitize an identifier. Useful when we get a possibly sanitized identifier from Spark or
    somewhere else, but we need an unsanitized one.
    Note: This function does not check the correctness of the identifier passed in. e.g. `foo``
    is not a valid sanitized identifier. When given such invalid input, this function returns
    invalid output.
    """
    if len(identifier) >= 2 and identifier[0] == "`" and identifier[-1] == "`":
        return identifier[1:-1].replace("``", "`")
    else:
        return identifier


# strings containing \ or ' can break sql statements, so escape them.
def escape_sql_string(input_str: str) -> str:
    return input_str.replace("\\", "\\\\").replace("'", "\\'")


def get_unique_list_order(elements: List[Any]) -> List[Any]:
    """
    Returns unique elements in the order they first appear.
    """
    return list(dict.fromkeys(elements))


def validate_database(database_name):
    if database_name is None:
        database_name = os.environ.get(constants.WEDATA_DEFAULT_FEATURE_STORE_DATABASE)
    if database_name is None:
        raise ValueError("Database_name variable or default database is not set.")
    return True