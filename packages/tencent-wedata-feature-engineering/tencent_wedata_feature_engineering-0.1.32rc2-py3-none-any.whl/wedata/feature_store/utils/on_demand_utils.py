import copy
from typing import Dict, List

from pyspark.sql import DataFrame
from pyspark.sql.functions import expr

from wedata.feature_store.entities.feature_function import FeatureFunction
from wedata.feature_store.entities.function_info import FunctionInfo
from wedata.feature_store.entities.on_demand_column_info import OnDemandColumnInfo
from wedata.feature_store.utils import common_utils, uc_utils


def _udf_expr(udf_name: str, arguments: List[str]) -> expr:
    """
    Generate a Spark SQL expression, e.g. expr("udf_name(col1, col2)")
    """
    arguments_str = ", ".join(common_utils.sanitize_identifiers(arguments))
    return expr(f"{udf_name}({arguments_str})")


def _validate_apply_functions_df(
    df: DataFrame,
    functions_to_apply: List[OnDemandColumnInfo],
    uc_function_infos: Dict[str, FunctionInfo],
):
    """
    Validate the following:
    1. On-demand input columns specified by functions_to_apply exist in the DataFrame.
    2. On-demand input columns have data types that match those of UDF parameters.
    """
    for odci in functions_to_apply:
        function_info = uc_function_infos[odci.udf_name]
        types_dict = dict(df.dtypes)

        for p in function_info.input_params:
            arg_column = odci.input_bindings[p.name]
            if arg_column not in df.columns:
                raise ValueError(
                    f"FeatureFunction argument column '{arg_column}' for UDF '{odci.udf_name}' parameter '{p.name}' "
                    f"does not exist in provided DataFrame with schema '{df.schema}'."
                )
            if types_dict[arg_column] != p.type_text:
                raise ValueError(
                    f"FeatureFunction argument column '{arg_column}' for UDF '{odci.udf_name}' parameter '{p.name}' "
                    f"does not have the expected type. Argument column '{arg_column}' has type "
                    f"'{types_dict[arg_column]}' and parameter '{p.name}' has type '{p.type_text}'."
                )


def apply_functions_if_not_overridden(
    df: DataFrame,
    functions_to_apply: List[OnDemandColumnInfo],
    uc_function_infos: Dict[str, FunctionInfo],
) -> DataFrame:
    """
    For all on-demand features, in the order defined by the FeatureSpec:
    If the feature does not already exist, append the evaluated UDF expression.
    Existing column values or column positions are not modified.

    `_validate_apply_functions_df` validates UDFs can be applied on `df` schema.

    The caller should validate:
    1. FeatureFunction bound argument columns for UDF parameters exist in FeatureSpec defined features.
    2. FeatureFunction output feature names are unique.
    """
    _validate_apply_functions_df(
        df=df,
        functions_to_apply=functions_to_apply,
        uc_function_infos=uc_function_infos,
    )

    columns = {}
    for odci in functions_to_apply:
        if odci.output_name not in df.columns:
            function_info = uc_function_infos[odci.udf_name]
            # Resolve the bound arguments in the UDF parameter order
            udf_arguments = [
                odci.input_bindings[p.name] for p in function_info.input_params
            ]
            columns[odci.output_name] = _udf_expr(odci.udf_name, udf_arguments)
    return df.withColumns(columns)


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
