import copy
from typing import List, Union

from wedata.feature_store.entities.feature_function import FeatureFunction
from wedata.feature_store.entities.feature_lookup import FeatureLookup
from wedata.feature_store.spark_client.spark_client import SparkClient
from wedata.feature_store.utils import uc_utils
from wedata.feature_store.utils.feature_lookup_utils import get_feature_lookups_with_full_table_names


def format_feature_lookups_and_functions(
        _spark_client: SparkClient, features: List[Union[FeatureLookup, FeatureFunction]]
):
    fl_idx = []
    ff_idx = []
    feature_lookups = []
    feature_functions = []
    for idx, feature in enumerate(features):
        if isinstance(feature, FeatureLookup):
            fl_idx.append(idx)
            feature_lookups.append(feature)
        elif isinstance(feature, FeatureFunction):
            ff_idx.append(idx)
            feature_functions.append(feature)
        else:
            raise ValueError(
                f"Expected a list of FeatureLookups for 'feature_lookups', but received type '{type(feature)}'."
            )

    # FeatureLookups and FeatureFunctions must have fully qualified table, UDF names
    feature_lookups = get_feature_lookups_with_full_table_names(
        feature_lookups,
        _spark_client.get_current_catalog(),
        _spark_client.get_current_database(),
    )
    feature_functions = get_feature_functions_with_full_udf_names(
        feature_functions,
        _spark_client.get_current_catalog(),
        _spark_client.get_current_database(),
    )

    # Restore original order of FeatureLookups, FeatureFunctions. Copy to avoid mutating original list.
    features = features.copy()
    for idx, feature in zip(fl_idx + ff_idx, feature_lookups + feature_functions):
        features[idx] = feature

    return features


def get_feature_functions_with_full_udf_names(
        feature_functions: List[FeatureFunction], current_catalog: str, current_schema: str
):
    """
    Takes in a list of FeatureFunctions, and returns copies with:
    1. Fully qualified UDF names.
    2. If output_name is empty, fully qualified UDF names as output_name.
    """
    udf_names = {ff.udf_name for ff in feature_functions}
    uc_utils._check_qualified_udf_names(udf_names)
    uc_utils._verify_all_udfs_in_uc(udf_names, current_catalog, current_schema)

    standardized_feature_functions = []
    for ff in feature_functions:
        ff_copy = copy.deepcopy(ff)
        del ff

        ff_copy._udf_name = uc_utils.get_full_udf_name(
            ff_copy.udf_name, current_catalog, current_schema
        )
        if not ff_copy.output_name:
            ff_copy._output_name = ff_copy.udf_name
        standardized_feature_functions.append(ff_copy)
    return standardized_feature_functions
