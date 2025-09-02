import copy
import datetime
import logging
from typing import Dict, List, Optional, Union

from wedata.feature_store.utils import common_utils

_logger = logging.getLogger(__name__)


class FeatureLookup:

    """
    特征查找类

    特征查找类用于指定特征表中的特征，并将其与训练集中的特征进行关联。

    特征查找类有以下属性：

    - table_name：特征表的名称。
    - lookup_key：用于在特征表和训练集之间进行联接的键。lookup_key必须是训练集中的列。lookup_key的类型和顺序必须与特征表的主键匹配。
    - feature_names：要从特征表中查找的特征的名称。如果您的模型需要主键作为特征，则可以将它们声明为独立的FeatureLookups。
    - rename_outputs：如果提供，则会将特征重命名为 :meth:`create_training_set() <databricks.feature_engineering.client.FeatureEngineeringClient.create_training_set>`返回的 :class:`TrainingSet <databricks.ml_features.training_set.TrainingSet>` 中的特征。
    - timestamp_lookup_key：用于在特征表和训练集之间进行联接的时间戳键。timestamp_lookup_key必须是训练集中的列。timestamp_lookup_key的类型必须与特征表的时间戳键的类型匹配。
    - lookback_window: 当对特征表执行时间点查找时使用的回溯窗口，该查找针对传递给 :meth:`create_training_set() <databricks.feature_engineering.client.FeatureEngineeringClient.create_training_set>` 方法的数据帧。特征存储将检索在数据帧的``timestamp_lookup_key``指定时间戳之前且在``lookback_window``时间范围内的最新特征值，如果不存在这样的特征值则返回null。当设置为0时，仅返回特征表中的精确匹配项。
    - feature_name：特征名称。**已弃用**。使用 `feature_names`。
    - output_name：如果提供，则会将此特征重命名为 :meth:`create_training_set() <databricks.feature_engineering.client.FeatureEngineeringClient.create_training_set>` 返回的 :class:`TrainingSet <databricks.ml_features.training_set.TrainingSet>` 中的特征。**已弃用**。使用 `rename_outputs`。

    示例：

    from databricks.feature_store import FeatureLookup

    lookup = FeatureLookup(
        table_name="my_feature_table",
        lookup_key="my_lookup_key",
        feature_names=["my_feature_1", "my_feature_2"],
        rename_outputs={"my_feature_1": "my_feature_1_renamed"},
        timestamp_lookup_key="my_timestamp_lookup_key",
        lookback_window=datetime.timedelta(days=1)
    )

    """

    def __init__(
        self,
        table_name: str,
        lookup_key: Union[str, List[str]],
        *,
        feature_names: Union[str, List[str], None] = None,
        rename_outputs: Optional[Dict[str, str]] = None,
        timestamp_lookup_key: Optional[str] = None,
        lookback_window: Optional[datetime.timedelta] = None,
        **kwargs,
    ):
        """Initialize a FeatureLookup object. See class documentation."""

        self._feature_name_deprecated = kwargs.pop("feature_name", None)
        self._output_name_deprecated = kwargs.pop("output_name", None)

        if kwargs:
            raise TypeError(
                f"FeatureLookup got unexpected keyword argument(s): {list(kwargs.keys())}"
            )

        self._table_name = table_name

        if type(timestamp_lookup_key) is list:
            if len(timestamp_lookup_key) == 0:
                timestamp_lookup_key = None
            elif len(timestamp_lookup_key) == 1:
                timestamp_lookup_key = timestamp_lookup_key[0]
            else:
                raise ValueError(
                    f"Setting multiple timestamp lookup keys is not supported."
                )

        if rename_outputs is not None and not isinstance(rename_outputs, dict):
            raise ValueError(
                f"Unexpected type for rename_outputs: {type(rename_outputs)}"
            )

        self._feature_names = common_utils.as_list(feature_names, default=[])

        # Make sure the user didn't accidentally pass in any nested lists/dicts in feature_names
        for fn in self._feature_names:
            if not isinstance(fn, str):
                raise ValueError(
                    f"Unexpected type for element in feature_names: {type(self._feature_names)}, only strings allowed in list"
                )

        if lookback_window is not None:
            if not timestamp_lookup_key:
                raise ValueError(
                    f"Unexpected lookback_window value: {lookback_window}, lookback windows can only be applied on time series "
                    f"feature tables. Use timestamp_lookup_key to perform point-in-time lookups with lookback window."
                )
            if not isinstance(
                lookback_window, datetime.timedelta
            ) or lookback_window < datetime.timedelta(0):
                raise ValueError(
                    f"Unexpected value for lookback_window: {lookback_window}, only non-negative datetime.timedelta allowed."
                )

        self._lookup_key = copy.copy(lookup_key)
        self._timestamp_lookup_key = copy.copy(timestamp_lookup_key)
        self._lookback_window = copy.copy(lookback_window)

        self._rename_outputs = {}
        if rename_outputs is not None:
            self._rename_outputs = rename_outputs.copy()

        self._inject_deprecated_feature_name()
        self._inject_deprecated_output_name()

    @property
    def table_name(self):
        """The table name to use in this FeatureLookup."""
        return self._table_name

    @property
    def lookup_key(self):
        """The lookup key(s) to use in this FeatureLookup."""
        return self._lookup_key

    @property
    def feature_name(self):
        """The feature name to use in this FeatureLookup. **Deprecated**. Use `feature_names`."""
        return self._feature_name_deprecated

    @property
    def feature_names(self):
        """The feature names to use in this FeatureLookup."""
        return self._feature_names

    @property
    def output_name(self):
        """The output name to use in this FeatureLookup. **Deprecated**. Use `feature_names`."""
        if self._output_name_deprecated:
            return self._output_name_deprecated
        else:
            return self._feature_name_deprecated

    @property
    def timestamp_lookup_key(self):
        return self._timestamp_lookup_key

    @property
    def lookback_window(self):
        """A lookback window applied only for point-in-time lookups."""
        return self._lookback_window

    def _get_feature_names(self):
        return self._feature_names

    def _get_output_name(self, feature_name):
        """Lookup the renamed output, or fallback to the feature name itself if no mapping is present"""
        return self._rename_outputs.get(feature_name, feature_name)

    def _inject_deprecated_feature_name(self):
        if self._feature_name_deprecated:
            if len(self._feature_names) > 0:
                raise ValueError(
                    "Use either feature_names or feature_name parameter, but not both."
                )
            _logger.warning(
                f'The feature_name parameter is deprecated. Use "feature_names".'
            )
            self._feature_names = [self._feature_name_deprecated]

    def _inject_deprecated_output_name(self):
        if len(self._feature_names) == 1 and self._output_name_deprecated:
            if len(self._rename_outputs) > 0:
                raise ValueError(
                    "Use either output_name or rename_outputs parameter, but not both."
                )
            _logger.warning(
                f'The output_name parameter is deprecated.  Use "rename_outputs".'
            )
            self._rename_outputs[self._feature_names[0]] = self._output_name_deprecated

    @table_name.setter
    def table_name(self, value):
        self._table_name = value
