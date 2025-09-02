"""
Wedata FeatureStoreClient Python实现
"""

from __future__ import annotations

from types import ModuleType
from typing import Union, List, Dict, Optional, Any
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.streaming import StreamingQuery
from pyspark.sql.types import StructType
import mlflow
from wedata.feature_store.constants.constants import FEATURE_STORE_CLIENT

from wedata.feature_store.constants.constants import APPEND, DEFAULT_WRITE_STREAM_TRIGGER
from wedata.feature_store.entities.feature_function import FeatureFunction
from wedata.feature_store.entities.feature_lookup import FeatureLookup
from wedata.feature_store.entities.feature_table import FeatureTable
from wedata.feature_store.entities.training_set import TrainingSet
from wedata.feature_store.feature_table_client.feature_table_client import FeatureTableClient
from wedata.feature_store.spark_client.spark_client import SparkClient
from wedata.feature_store.training_set_client.training_set_client import TrainingSetClient
from wedata.feature_store.utils import common_utils
from wedata.feature_store.utils.feature_utils import format_feature_lookups_and_functions


class FeatureStoreClient:
    """特征存储统一客户端，提供特征全生命周期管理能力"""

    def __init__(self, spark: Optional[SparkSession] = None):
        """
        :param spark: 已初始化的SparkSession对象
        """
        if spark is None:
            spark = SparkSession.builder.getOrCreate()
        self._spark = spark
        self._spark_client = SparkClient(spark)
        self._feature_table_client = FeatureTableClient(spark)
        self._training_set_client = TrainingSetClient(self._spark_client)

    def create_table(
            self,
            name: str,
            primary_keys: Union[str, List[str]],
            database_name: Optional[str] = None,
            location: Optional[str] = None,
            df: Optional[DataFrame] = None,
            *,
            timestamp_keys: Union[str, List[str], None] = None,
            partition_columns: Union[str, List[str], None] = None,
            schema: Optional[StructType] = None,
            description: Optional[str] = None,
            tags: Optional[Dict[str, str]] = None
    ) -> FeatureTable:
        """
        创建特征表（支持批流数据写入）

        Args:
            name: 特征表全称（格式：<table>）
            primary_keys: 主键列名（支持复合主键）
            database_name: 数据库名
            location: cos存储位置
            df: 初始数据（可选，用于推断schema）
            timestamp_keys: 时间戳键（用于时态特征）
            partition_columns: 分区列（优化存储查询）
            schema: 表结构定义（可选，当不提供df时必需）
            description: 业务描述
            tags: 业务标签

        Returns:
            FeatureTable实例

        Raises:
            ValueError: 当schema与数据不匹配时
        """

        return self._feature_table_client.create_table(
            name=name,
            primary_keys=primary_keys,
            database_name=database_name,
            location=location,
            df=df,
            timestamp_keys=timestamp_keys,
            partition_columns=partition_columns,
            schema=schema,
            description=description,
            tags=tags
        )

    def register_table(self, name: str, database_name: Optional[str] = None) -> DataFrame:
        """
        读取特征表数据

        Args:
            name: 特征表名称
            database_name: 特征库名称

        Returns:
            DataFrame: 包含特征表数据的DataFrame对象
        """

        return self._feature_table_client.register_table(name, database_name)

    def read_table(self, name: str, database_name: Optional[str] = None) -> DataFrame:
        """
        读取特征表数据

        Args:
            name: 特征表名称
            database_name: 特征库名称

        Returns:
            DataFrame: 包含特征表数据的DataFrame对象
        """

        return self._feature_table_client.read_table(name, database_name)

    def get_table(self, name: str, database_name: Optional[str] = None) -> FeatureTable:
        """
        获取特征表元数据
        Args:
            name: 特征表名称
            database_name: 特征库名称

        Returns:
            FeatureTable: 包含特征表元数据的FeatureTable对象
        """

        return self._feature_table_client.get_table(name, self._spark_client, database_name)

    def drop_table(self, name: str, database_name: Optional[str] = None) -> None:
        """
        删除特征表

        Args:
            name: 要删除的特征表名称
            database_name: database name

        Returns:
            None
        """

        return self._feature_table_client.drop_table(name, database_name)

    def write_table(
            self,
            name: str,
            df: DataFrame,
            database_name: Optional[str] = None,
            mode: Optional[str] = APPEND,
            checkpoint_location: Optional[str] = None,
            trigger: Dict[str, Any] = DEFAULT_WRITE_STREAM_TRIGGER,
    ) -> Optional[StreamingQuery]:
        """
        写入数据到特征表（支持批处理和流式处理）

        Args:
            name: 特征表名称
            df: 要写入的数据DataFrame
            database_name: 特征库名称
            mode: 写入模式（默认追加）
            checkpoint_location: 流式处理的检查点位置（可选）
            trigger: 流式处理触发器配置（默认使用系统预设）

        Returns:
            如果是流式写入返回StreamingQuery对象，否则返回None
        """

        return self._feature_table_client.write_table(
            name=name,
            df=df,
            database_name=database_name,
            mode=mode,
            checkpoint_location=checkpoint_location,
            trigger=trigger,
        )

    def create_training_set(
            self,
            df: DataFrame,
            feature_lookups: List[Union[FeatureLookup, FeatureFunction]],
            label: Union[str, List[str], None],
            exclude_columns: Optional[List[str]] = None,
            database_name: Optional[str] = None,
            **kwargs,
    ) -> TrainingSet:
        """
        创建训练集

        Args:
            df: 基础数据
            feature_lookups: 特征查询列表
            label: 标签列名
            exclude_columns: 排除列名
            database_name: database name

        Returns:
            TrainingSet实例
        """

        if exclude_columns is None:
            exclude_columns = []

        # 如果为FeatureLookup，则将需要校验FeatureLookup的table_name，并构建完整表名
        for feature in feature_lookups:
            if isinstance(feature, FeatureLookup):
                if not feature.table_name:
                    raise ValueError("FeatureLookup must specify a table_name")
                # 先校验表名格式是否合法
                common_utils.validate_table_name(feature.table_name)
                # 再构建完整表名，并赋值给FeatureLookup对象
                feature.table_name = common_utils.build_full_table_name(feature.table_name, database_name)

        features = feature_lookups
        del feature_lookups

        features = format_feature_lookups_and_functions(self._spark_client, features)

        return self._training_set_client.create_training_set_from_feature_lookups(
            df=df,
            feature_lookups=features,
            label=label,
            exclude_columns=exclude_columns,
            **kwargs
        )

    def log_model(
            self,
            model: Any,
            artifact_path: str,
            *,
            flavor: ModuleType,
            training_set: Optional[TrainingSet] = None,
            registered_model_name: Optional[str] = None,
            model_registry_uri: Optional[str] = None,
            await_registration_for: int = mlflow.tracking._model_registry.DEFAULT_AWAIT_MAX_SLEEP_SECONDS,
            infer_input_example: bool = False,
            **kwargs,
    ):
        """
         记录MLflow模型并关联特征查找信息

         注意：必须使用TrainingSet.load_df返回的DataFrame训练模型，
         任何对DataFrame的修改(如标准化、添加列等)都不会在推理时应用

         Args:
             model: 要记录的模型对象
             artifact_path: 模型存储路径
             flavor: MLflow模型类型模块(如mlflow.sklearn)
             training_set: 训练模型使用的TrainingSet对象(可选)
             registered_model_name: 要注册的模型名称(可选)
             model_registry_uri: 模型注册中心地址(可选)
             await_registration_for: 等待模型注册完成的秒数(默认300秒)
             infer_input_example: 是否自动记录输入示例(默认False)

         Returns:
             None
         """

        self._training_set_client.log_model(
            model=model,
            artifact_path=artifact_path,
            flavor=flavor,
            training_set=training_set,
            registered_model_name=registered_model_name,
            model_registry_uri=model_registry_uri,
            await_registration_for=await_registration_for,
            infer_input_example=infer_input_example,
            **kwargs
        )

    def score_batch(
        self, model_uri: str, df: DataFrame, result_type: str = "double"
    ) -> DataFrame:
        """
        Evaluate the model on the provided :class:`DataFrame <pyspark.sql.DataFrame>`.

        Additional features required for
        model evaluation will be automatically retrieved from :mod:`Feature Store <databricks.feature_store.client>`.

        .. todo::

           [ML-15539]: Replace the bitly URL in doc string

        The model must have been logged with :meth:`.FeatureStoreClient.log_model`,
        which packages the model with feature metadata. Unless present in ``df``,
        these features will be looked up from :mod:`Feature Store <databricks.feature_store.client>` and joined with ``df``
        prior to scoring the model.

        If a feature is included in ``df``, the provided feature values will be used rather
        than those stored in :mod:`Feature Store <databricks.feature_store.client>`.

        For example, if a model is trained on two features ``account_creation_date`` and
        ``num_lifetime_purchases``, as in:

        .. code-block:: python

            feature_lookups = [
                FeatureLookup(
                    table_name = 'trust_and_safety.customer_features',
                    feature_name = 'account_creation_date',
                    lookup_key = 'customer_id',
                ),
                FeatureLookup(
                    table_name = 'trust_and_safety.customer_features',
                    feature_name = 'num_lifetime_purchases',
                    lookup_key = 'customer_id'
                ),
            ]

            with mlflow.start_run():
                training_set = fs.create_training_set(
                    df,
                    feature_lookups = feature_lookups,
                    label = 'is_banned',
                    exclude_columns = ['customer_id']
                )
                ...
                  fs.log_model(
                    model,
                    "model",
                    flavor=mlflow.sklearn,
                    training_set=training_set,
                    registered_model_name="example_model"
                  )

        Then at inference time, the caller of :meth:`FeatureStoreClient.score_batch` must pass
        a :class:`DataFrame <pyspark.sql.DataFrame>` that includes ``customer_id``, the ``lookup_key`` specified in the
        ``FeatureLookups`` of the :mod:`training_set <databricks.feature_engineering.training_set>`.
        If the :class:`DataFrame <pyspark.sql.DataFrame>` contains a column
        ``account_creation_date``, the values of this column will be used
        in lieu of those in :mod:`Feature Store <databricks.feature_store.client>`. As in:

        .. code-block:: python

            # batch_df has columns ['customer_id', 'account_creation_date']
            predictions = fs.score_batch(
                'models:/example_model/1',
                batch_df
            )

        :param model_uri: The location, in URI format, of the MLflow model logged using
          :meth:`FeatureStoreClient.log_model`. One of:

            * ``runs:/<mlflow_run_id>/run-relative/path/to/model``

            * ``models:/<model_name>/<model_version>``

            * ``models:/<model_name>/<stage>``

          For more information about URI schemes, see
          `Referencing Artifacts <https://bit.ly/3wnrseE>`_.
        :param df: The :class:`DataFrame <pyspark.sql.DataFrame>` to score the model on. :mod:`Feature Store <databricks.feature_store.client>` features will be joined with
          ``df`` prior to scoring the model. ``df`` must:

              1. Contain columns for lookup keys required to join feature data from Feature
              Store, as specified in the ``feature_spec.yaml`` artifact.

              2. Contain columns for all source keys required to score the model, as specified in
              the ``feature_spec.yaml`` artifact.

              3. Not contain a column ``prediction``, which is reserved for the model's predictions.
              ``df`` may contain additional columns.

          Streaming DataFrames are not supported.

        :param result_type: The return type of the model.
           See :func:`mlflow.pyfunc.spark_udf` result_type.
        :return: A :class:`DataFrame <pyspark.sql.DataFrame>`
           containing:

            1. All columns of ``df``.

            2. All feature values retrieved from Feature Store.

            3. A column ``prediction`` containing the output of the model.

        """
        return self._training_set_client.score_batch(
            model_uri=model_uri,
            df=df,
            result_type=result_type,
            client_name=FEATURE_STORE_CLIENT,
        )

    @property
    def spark(self):
        return self._spark
