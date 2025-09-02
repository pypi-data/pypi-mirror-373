from collections import defaultdict
from typing import Optional, Any, Dict, List

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.catalog import Column
from pyspark.sql.functions import when, isnull
from pyspark.sql.types import StructType, StringType, StructField
from mlflow.pyfunc import spark_udf

from wedata.feature_store.constants.constants import (
    _PREBUILT_ENV_URI
)

from wedata.feature_store.entities.feature import Feature
from wedata.feature_store.entities.feature_table import FeatureTable
from wedata.feature_store.entities.function_info import FunctionParameterInfo, FunctionInfo
from wedata.feature_store.utils.common_utils import unsanitize_identifier


class SparkClient:
    def __init__(self, spark: SparkSession):
        self._spark = spark

    def get_current_catalog(self):
        """
        获取当前Spark会话的catalog名称（使用spark.catalog.currentCatalog属性）

        返回:
            str: 当前catalog名称，如果未设置则返回None
        """
        try:
            return unsanitize_identifier(self._spark.catalog.currentCatalog())
        except Exception:
            return None

    def get_current_database(self):
        """
        获取Spark上下文中当前设置的数据库名称

        返回:
            str: 当前数据库名称，如果获取失败则返回None
        """
        try:
            # 使用Spark SQL查询当前数据库
            df = self._spark.sql("SELECT CURRENT_DATABASE()")
            # 获取第一行第一列的值并去除特殊字符
            return unsanitize_identifier(df.first()[0])
        except Exception:
            # 捕获所有异常并返回None
            return None




    def createDataFrame(self, data, schema) -> DataFrame:
        return self._spark.createDataFrame(data, schema)


    def read_table(self, table_name):
        """读取Spark表数据

        Args:
            table_name: 表名，支持格式: catalog.schema.table、schema.table

        Returns:
            DataFrame: 表数据

        Raises:
            ValueError: 当表不存在或读取失败时抛出
        """
        try:
            # 验证表是否存在
            if not self._spark.catalog.tableExists(table_name):
                raise ValueError(f"Table does not exist: {table_name}")

            return self._spark.table(table_name)

        except Exception as e:
            raise ValueError(f"Failed to read table {table_name}: {str(e)}")


    def get_features(self, table_name):
        # 查询列信息
        columns = self._spark.catalog.listColumns(tableName=table_name)
        return [
            Feature(
                feature_table=table_name,
                feature_id=f"{table_name}_{row.name}",
                name=row.name,
                data_type=row.dataType,
                description=row.description or ""
            ) for row in columns
        ]

    def get_feature_table(self, table_name):
        # 获取表元数据
        table = self._spark.catalog.getTable(table_name)

        # 获取表配置信息
        properties = self._spark.sql(f"SHOW TBLPROPERTIES {table_name}").collect()
        primary_key_str = next((row.value for row in properties if row.key == "primaryKeys"), None)
        primary_keys = primary_key_str.split(",") if primary_key_str else []
        table_id = next((row.value for row in properties if row.key == "table_id"), table_name)
        description = table.description or next((row.value for row in properties if row.key == "comment"), None)
        timestamp_keys_str = next((row.value for row in properties if row.key == "timestampKeys"), None)
        timestamp_keys = timestamp_keys_str.split(",") if timestamp_keys_str else []
        # 获取分区字段信息
        desc_df = self._spark.sql(f"DESCRIBE EXTENDED {table_name}")
        partition_info = desc_df.filter("col_name LIKE '_partition%'").collect()
        partition_columns = []
        if partition_info:
            partition_str = partition_info[0]["data_type"]
            # 从分区字符串中提取分区字段
            if partition_str.startswith("struct<") and partition_str.endswith(">"):
                # 去掉struct<>外壳
                fields_str = partition_str[7:-1]
                # 分割各个字段定义
                field_defs = [f.strip() for f in fields_str.split(",") if f.strip()]
                # 提取字段名
                partition_columns = [f.split(":")[0].strip() for f in field_defs]

        # 获取特征列信息
        features = self.get_features(table_name)

        # 构建完整的FeatureTable对象
        return FeatureTable(
            name=table_name,
            table_id=table_id,
            description=description,
            primary_keys=primary_keys,
            partition_columns=partition_columns,
            features=features,
            creation_timestamp=None,  # Spark表元数据不包含创建时间戳
            online_stores=None,
            notebook_producers=None,
            job_producers=None,
            table_data_sources=None,
            path_data_sources=None,
            custom_data_sources=None,
            timestamp_keys=timestamp_keys,
            tags=None
        )

    def _get_routines_with_parameters(self, full_routine_names: List[str]) -> DataFrame:
        """
        Retrieve the routines with their parameters from information_schema.routines, information_schema.parameters.
        Return DataFrame only contains routines that 1. exist and 2. the caller has GetFunction permission on.

        Note: The returned DataFrame contains the cartesian product of routines and parameters.
        For efficiency, routines table columns are only present in the first row for each routine.
        """
        routine_name_schema = StructType(
            [
                StructField("specific_catalog", StringType(), False),
                StructField("specific_schema", StringType(), False),
                StructField("specific_name", StringType(), False),
            ]
        )
        routine_names_df = self.createDataFrame(
            [full_routine_name.split(".") for full_routine_name in full_routine_names],
            routine_name_schema,
        )
        routines_table = self.read_table(
            "system.information_schema.routines"
        )
        parameters_table = self.read_table(
            "system.information_schema.parameters"
        )

        # Inner join routines table to filter out non-existent routines.
        # Left join parameters as routines may have no parameters.
        full_routines_with_parameters_df = routine_names_df.join(
            routines_table, on=routine_names_df.columns, how="inner"
        ).join(parameters_table, on=routine_names_df.columns, how="left")

        # Return only relevant metadata from information_schema, sorted by routine name + parameter order.
        # For efficiency, only preserve routine column values in the first of each routine's result rows.
        # The first row will have parameter.ordinal_value is None (no parameters) or equals 0 (first parameter).
        def select_if_first_row(col: Column) -> Column:
            return when(
                isnull(parameters_table.ordinal_position)
                | (parameters_table.ordinal_position == 0),
                col,
                ).otherwise(None)

        return full_routines_with_parameters_df.select(
            routine_names_df.columns
            + [
                select_if_first_row(routines_table.routine_definition).alias(
                    "routine_definition"
                ),
                select_if_first_row(routines_table.external_language).alias(
                    "external_language"
                ),
                parameters_table.ordinal_position,
                parameters_table.parameter_name,
                parameters_table.full_data_type,
            ]
        ).sort(routine_names_df.columns + [parameters_table.ordinal_position])

    def get_functions(self, full_function_names: List[str]) -> List[FunctionInfo]:
        """
        Retrieves and maps Unity Catalog functions' metadata as FunctionInfos.
        """
        # Avoid unnecessary Spark calls and return if empty.
        if not full_function_names:
            return []

        # Collect dict of routine name -> DataFrame rows describing the routine.
        routines_with_parameters_df = self._get_routines_with_parameters(
            full_routine_names=full_function_names
        )
        routine_infos = defaultdict(list)
        for r in routines_with_parameters_df.collect():
            routine_name = f"{r.specific_catalog}.{r.specific_schema}.{r.specific_name}"
            routine_infos[routine_name].append(r)

        # Mock GetFunction DNE error, since information_schema does not throw.
        for function_name in full_function_names:
            if not function_name in routine_infos:
                raise ValueError(f"Function '{function_name}' does not exist.")

        # Map routine_infos into FunctionInfos.
        function_infos = []
        for function_name in full_function_names:
            routine_info = routine_infos[function_name][0]
            input_params = [
                FunctionParameterInfo(name=p.parameter_name, type_text=p.full_data_type)
                for p in routine_infos[function_name]
                if p.ordinal_position is not None
            ]
            function_infos.append(
                FunctionInfo(
                    full_name=function_name,
                    input_params=input_params,
                    routine_definition=routine_info.routine_definition,
                    external_language=routine_info.external_language,
                )
            )
        return function_infos

    def get_predict_udf(
        self,
        model_uri,
        result_type=None,
        env_manager=None,
        params: Optional[dict[str, Any]] = None,
        prebuilt_env_uri: Optional[str] = None,
    ):
        kwargs = {}
        if result_type:
            kwargs["result_type"] = result_type
        if env_manager:
            kwargs["env_manager"] = env_manager
        if params:
            kwargs["params"] = params
        if prebuilt_env_uri:
            kwargs[_PREBUILT_ENV_URI] = prebuilt_env_uri

        return spark_udf(self._spark, model_uri, **kwargs)
