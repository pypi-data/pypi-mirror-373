from typing import Dict, Optional


class FeatureFunction:

    """
     特征方法类

     特征方法是用户定义的函数，用于将特征表中的特征组合成新特征，特征方法可以是任何用户定义的函数，例如Python UDF。

    特征方法类有以下属性：
    - udf_name：要调用的Python UDF的名称。
    - input_bindings：用于将Python UDF的输入映射到训练集中的特征的字典。
    - output_name：如果提供，则会将此特征重命名为 :meth:`create_training_set() <databricks.feature_engineering.client.FeatureEngineeringClient.create_training_set>` 返回的 :class:`TrainingSet <databricks.ml_features.training_set.TrainingSet>` 中的特征。

    """

    def __init__(
        self,
        *,
        udf_name: str,
        input_bindings: Optional[Dict[str, str]] = None,
        output_name: Optional[str] = None,
    ):
        """Initialize a FeatureFunction object. See class documentation."""
        # UC function names are always lowercase.
        self._udf_name = udf_name.lower()
        self._input_bindings = input_bindings if input_bindings else {}
        self._output_name = output_name

    @property
    def udf_name(self) -> str:
        """
        The name of the Python UDF called by this FeatureFunction.
        """
        return self._udf_name

    @property
    def input_bindings(self) -> Dict[str, str]:
        """
        The input to use for each argument of the Python UDF.

        For example:

        `{"x": "feature1", "y": "input1"}`
        """
        return self._input_bindings

    @property
    def output_name(self) -> Optional[str]:
        """
        The output name to use for the results of this FeatureFunction.
        If empty, defaults to the fully qualified `udf_name` when evaluated.
        """
        return self._output_name
