from typing import Dict, List, Optional

from pyspark.sql import DataFrame

from wedata.feature_store.entities.feature_table import FeatureTable
from wedata.feature_store.entities.function_info import FunctionInfo
from wedata.feature_store.utils.feature_lookup_utils import (
    join_feature_data_if_not_overridden,
)

from wedata.feature_store.entities.feature_spec import FeatureSpec
from wedata.feature_store.utils.feature_spec_utils import (
    COLUMN_INFO_TYPE_FEATURE,
    COLUMN_INFO_TYPE_ON_DEMAND,
    COLUMN_INFO_TYPE_SOURCE,
    get_feature_execution_groups,
)
from wedata.feature_store.utils.on_demand_utils import apply_functions_if_not_overridden


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
        # Perform basic validations and resolve FeatureSpec and label column data types.
        self._validate_and_inject_dtypes()
        self._label_data_types = {
            name: data_type for name, data_type in df.dtypes if name in labels
        }

    @property
    def feature_spec(self) -> FeatureSpec:
        """Define a feature spec."""
        return self._feature_spec

    def _augment_df(self) -> DataFrame:
        """
        Internal helper to augment DataFrame with feature lookups and on-demand features specified in the FeatureSpec.
        Does not drop excluded columns, and does not overwrite columns that already exist.
        Return column order is df.columns + feature lookups + on-demand features.
        """
        execution_groups = get_feature_execution_groups(
            self.feature_spec, self._df.columns
        )

        result_df = self._df
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
        # Return only included columns in order defined by FeatureSpec + labels
        included_columns = [
            ci.output_name for ci in self.feature_spec.column_infos if ci.include
        ] + self._labels
        return augmented_df.select(included_columns)
