import logging
from typing import List, Union, Any
from collections import Counter


from pyspark.sql import DataFrame

_logger = logging.getLogger(__name__)


def standardize_checkpoint_location(checkpoint_location):
    if checkpoint_location is None:
        return checkpoint_location
    checkpoint_location = checkpoint_location.strip()
    if checkpoint_location == "":
        checkpoint_location = None
    return checkpoint_location


def _is_spark_connect_data_frame(df):
    # We cannot directly pyspark.sql.connect.dataframe.DataFrame as it requires Spark 3.4, which
    # is not installed on DBR 12.2 and earlier. Instead, we string match on the type.
    return (
        type(df).__name__ == "DataFrame"
        and type(df).__module__ == "pyspark.sql.connect.dataframe"
    )


def check_dataframe_type(df):
    """
    Check if df is a PySpark DataFrame, otherwise raise an error.
    """
    if not (isinstance(df, DataFrame) or _is_spark_connect_data_frame(df)):
        raise ValueError(
            f"Unsupported DataFrame type: {type(df)}. DataFrame must be a PySpark DataFrame."
        )


def check_kwargs_empty(the_kwargs, method_name):
    if len(the_kwargs) != 0:
        raise TypeError(
            f"{method_name}() got unexpected keyword argument(s): {list(the_kwargs.keys())}"
        )


def check_duplicate_keys(keys: Union[str, List[str]], key_name: str) -> None:
    """
    Check if there are duplicate keys. Raise an error if there is duplicates.
    """
    if keys and isinstance(keys, list):
        seen = set()
        for k in keys:
            if k in seen:
                raise ValueError(
                    f"Found duplicated key '{k}' in {key_name}. {key_name} must be unique."
                )
            seen.add(k)

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
