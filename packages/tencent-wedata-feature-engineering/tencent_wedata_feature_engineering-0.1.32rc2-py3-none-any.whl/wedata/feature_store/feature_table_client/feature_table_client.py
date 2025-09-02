"""
特征表操作相关工具方法
"""
import json
from typing import Union, List, Dict, Optional, Sequence, Any
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.streaming import StreamingQuery
from pyspark.sql.types import StructType
import os

from wedata.feature_store.constants.constants import APPEND, DEFAULT_WRITE_STREAM_TRIGGER, FEATURE_TABLE_KEY, \
    FEATURE_TABLE_VALUE, FEATURE_TABLE_PROJECT
from wedata.feature_store.entities.feature_table import FeatureTable
from wedata.feature_store.spark_client.spark_client import SparkClient
from wedata.feature_store.utils import common_utils


class FeatureTableClient:
    """特征表操作类"""

    def __init__(
        self,
        spark: SparkSession
    ):
        self._spark = spark

    @staticmethod
    def _normalize_params(
            param: Optional[Union[str, Sequence[str]]],
            default_type: type = list
    ) -> list:
        """统一处理参数标准化"""
        if param is None:
            return default_type()
        return list(param) if isinstance(param, Sequence) else [param]

    @staticmethod
    def _validate_schema(df: DataFrame, schema: StructType):
        """校验DataFrame和schema的有效性和一致性"""
        # 检查是否同时为空
        if df is None and schema is None:
            raise ValueError("Either DataFrame or schema must be provided")

        # 检查schema匹配
        if df is not None and schema is not None:
            df_schema = df.schema
            if df_schema != schema:
                diff_fields = set(df_schema.fieldNames()).symmetric_difference(set(schema.fieldNames()))
                raise ValueError(
                    f"DataFrame schema does not match. Differences: "
                    f"{diff_fields if diff_fields else 'field type mismatch'}"
                )

    @staticmethod
    def _validate_key_conflicts(primary_keys: List[str], timestamp_keys: List[str]):
        """校验主键与时间戳键是否冲突"""
        conflict_keys = set(timestamp_keys) & set(primary_keys)
        if conflict_keys:
            raise ValueError(f"Timestamp keys conflict with primary keys: {conflict_keys}")

    @staticmethod
    def _escape_sql_value(value: str) -> str:
        """转义SQL值中的特殊字符"""
        return value.replace("'", "''")

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
            database_name: Optional[str] = None,
            location: Optional[str] = None,
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

        # 参数标准化
        primary_keys = self._normalize_params(primary_keys)
        timestamp_keys = self._normalize_params(timestamp_keys)
        partition_columns = self._normalize_params(partition_columns)

        # 元数据校验
        self._validate_schema(df, schema)
        self._validate_key_conflicts(primary_keys, timestamp_keys)

        # 表名校验
        common_utils.validate_table_name(name)

        common_utils.validate_database(database_name)

        # 构建完整表名
        table_name = common_utils.build_full_table_name(name, database_name)

        # 检查表是否存在
        try:
            if self._spark.catalog.tableExists(table_name):
                raise ValueError(
                    f"Table '{name}' already exists\n"
                    "Solutions:\n"
                    "1. Use a different table name\n"
                    "2. Drop the existing table: spark.sql(f'DROP TABLE {name}')\n"
                )
        except Exception as e:
            raise ValueError(f"Error checking table existence: {str(e)}") from e

        # 推断表schema
        table_schema = schema or df.schema

        # 构建时间戳键属性

        #从环境变量获取额外标签
        env_tags = {
            "project_id": os.getenv("WEDATA_PROJECT_ID", ""),  # wedata项目ID
            "engine_name": os.getenv("WEDATA_NOTEBOOK_ENGINE", ""),  # wedata引擎名称
            "user_uin": os.getenv("KERNEL_LOGIN_UIN", "")  # wedata用户UIN
        }
        projectId = os.getenv("WEDATA_PROJECT_ID", "")
        # 构建表属性（通过TBLPROPERTIES）
        tbl_properties = {
            "wedata.feature_table": "true",
            "primaryKeys": ",".join(primary_keys),
            "wedata.feature_project_id": f"{json.dumps([projectId])}",
            "timestampKeys": ",".join(timestamp_keys) if timestamp_keys else "",
            "comment": description or "",
            **{f"{k}": v for k, v in (tags or {}).items()},
            **{f"feature_{k}": v for k, v in (env_tags or {}).items()}
        }

        # 构建列定义
        columns_ddl = []
        for field in table_schema.fields:
            data_type = field.dataType.simpleString().upper()
            col_def = f"`{field.name}` {data_type}"
            if not field.nullable:
                col_def += " NOT NULL"
            # 添加字段注释(如果metadata中有comment)
            if field.metadata and "comment" in field.metadata:
                comment = self._escape_sql_value(field.metadata["comment"])
                col_def += f" COMMENT '{comment}'"
            columns_ddl.append(col_def)

        # 构建分区表达式
        partition_expr = (
            f"PARTITIONED BY ({', '.join([f'`{c}`' for c in partition_columns])})"
            if partition_columns else ""
        )
        # 本地调试 iceberg --》PARQUET
        # 核心建表语句
        ddl = f"""
        CREATE TABLE {table_name} (
            {', '.join(columns_ddl)}
        )
        USING iceberg
        {partition_expr}
        TBLPROPERTIES (
            {', '.join(f"'{k}'='{self._escape_sql_value(v)}'" for k, v in tbl_properties.items())}
        )
        """

        # 打印sql
        print(f"create table ddl: {ddl}\n")

        # 执行DDL
        try:
            self._spark.sql(ddl)
            if df is not None:
                df.write.insertInto(table_name)
        except Exception as e:
            raise ValueError(f"Failed to create table: {str(e)}") from e

        print(f"create table {name} done")

        # 构建并返回FeatureTable对象
        return FeatureTable(
            name=name,
            table_id=table_name,
            description=description or "",
            primary_keys=primary_keys,
            partition_columns=partition_columns or [],
            features=[field.name for field in table_schema.fields],
            timestamp_keys=timestamp_keys or [],
            tags=dict(**tags or {}, **env_tags)
        )

    def write_table(
            self,
            name: str,
            df: DataFrame,
            database_name: Optional[str] = None,
            mode: Optional[str] = APPEND,
            checkpoint_location: Optional[str] = None,
            trigger: Optional[Dict[str, Any]] = DEFAULT_WRITE_STREAM_TRIGGER
    ) -> Optional[StreamingQuery]:

        """
        写入特征表数据（支持批处理和流式写入）

        Args:
            name: 特征表名称（格式：<table>）
            df: 要写入的数据（DataFrame）
            database_name: 数据库名
            mode: 写入模式（append/overwrite）
            checkpoint_location: 流式写入的检查点位置（仅流式写入需要）
            trigger: 流式写入触发条件（仅流式写入需要）

        Returns:
            如果是流式写入返回StreamingQuery对象，否则返回None

        Raises:
            ValueError: 当参数不合法时抛出
        """

        # 验证写入模式
        valid_modes = ["append", "overwrite"]
        if mode not in valid_modes:
            raise ValueError(f"Invalid write mode '{mode}', valid options: {valid_modes}")

        # 表名校验
        common_utils.validate_table_name(name)

        common_utils.validate_database(database_name)

        # 构建完整表名
        table_name = common_utils.build_full_table_name(name, database_name)

        # 判断是否是流式DataFrame
        is_streaming = df.isStreaming

        try:
            if is_streaming:
                # 流式写入
                if not checkpoint_location:
                    raise ValueError("Streaming write requires checkpoint_location parameter")

                writer = df.writeStream \
                    .format("parquet") \
                    .outputMode(mode) \
                    .option("checkpointLocation", checkpoint_location)

                if trigger:
                    writer = writer.trigger(**trigger)

                return writer.toTable(table_name)
            else:
                # 批处理写入
                df.write \
                    .mode(mode) \
                    .insertInto(table_name)
                return None

        except Exception as e:
            raise ValueError(f"Failed to write to table '{table_name}': {str(e)}") from e


    def register_table(self, name, database_name):
        """注册表 为特征表
                Args:
                    name: 表名（格式：<table>）
                    database_name: 特征库名称

                Raises:
                    ValueError: 当表不存在或参数无效时抛出
                    RuntimeError: 当修改操作失败时抛出

                示例:
                    # 修改表属性
                    client.register_table("user_features", "user_database")
                """

        # 表名校验
        common_utils.validate_table_name(name)
        common_utils.validate_database(database_name)

        # 构建完整表名
        table_name = common_utils.build_full_table_name(name, database_name)

        try:
            # 检查表是否存在
            if not self._spark.catalog.tableExists(table_name):
                raise ValueError(f"table '{name}' not exists")
            tbl_pro = self._spark.sql(f"SHOW TBLPROPERTIES {table_name}")
            props = {row['key']: row['value'] for row in tbl_pro.collect()}
            s = props.get(FEATURE_TABLE_PROJECT, "")
            if not s:  # 如果s是空字符串
                projectIds = []
            else:
                projectIds = json.loads(s)
            current_project_id = os.getenv("WEDATA_PROJECT_ID")
            # 判断是否包含
            if current_project_id not in projectIds:
                register_table_project_ids = props.get(FEATURE_TABLE_PROJECT)
            else:
                projectIds.append(current_project_id)
                register_table_project_ids = json.dumps(projectIds)
            tbl_properties = {
                FEATURE_TABLE_KEY: FEATURE_TABLE_VALUE,
                FEATURE_TABLE_PROJECT: register_table_project_ids,
            }

            # 构建属性设置语句
            props_str = ", ".join(
                f"'{k}'='{self._escape_sql_value(v)}'"
                for k, v in tbl_properties
            )

            alter_sql = f"ALTER TABLE {table_name} SET TBLPROPERTIES ({props_str})"

            # 执行修改
            self._spark.sql(alter_sql)
            print(f"Successfully register table '{name}'")

        except ValueError as e:
            raise  # 直接抛出已知的ValueError
        except Exception as e:
            raise RuntimeError(f"Failed to modify properties for table '{name}': {str(e)}") from e


    def read_table(
                self,
                name: str,
                database_name: Optional[str] = None,
        ) -> DataFrame:

        """
        从特征表中读取数据

        Args:
            name: 特征表名称（格式：<table>）
            database_name: 特征库名称
        Returns:
            包含表数据的DataFrame

        Raises:
            ValueError: 当表不存在或读取失败时抛出
        """

        # 表名校验
        common_utils.validate_table_name(name)

        common_utils.validate_database(database_name)


        # 构建完整表名
        table_name = common_utils.build_full_table_name(name, database_name)

        try:
            # 检查表是否存在
            if not self._spark.catalog.tableExists(table_name):
                raise ValueError(f"Table '{name}' does not exist")

            # 读取表数据
            return self._spark.read.table(table_name)

        except Exception as e:
            raise ValueError(f"Failed to read table '{name}': {str(e)}") from e

    def drop_table(self, name: str, database_name: Optional[str] = None) -> None:

        """
        删除特征表（表不存在时抛出异常）

        Args:
            name: 特征表名称（格式：<table>）
            database_name: 特征库名称

        Raises:
            ValueError: 当表不存在时抛出
            RuntimeError: 当删除操作失败时抛出

        示例:
            # 基本删除
            drop_table("user_features")
        """

        # 表名校验
        common_utils.validate_table_name(name)

        # 构建完整表名
        table_name = common_utils.build_full_table_name(name, database_name)

        try:
            # 检查表是否存在
            if not self._spark.catalog.tableExists(table_name):
                print(f"Table '{name}' does not exist")
                return

            # 执行删除
            self._spark.sql(f"DROP TABLE {table_name}")
            print(f"Table '{name}' dropped")

        except ValueError as e:
            raise  # 直接抛出已知的ValueError
        except Exception as e:
            raise RuntimeError(f"Failed to delete table '{name}': {str(e)}") from e

    def get_table(
            self,
            name: str,
            spark_client: SparkClient,
            database_name: Optional[str] = None,
    ) -> FeatureTable:

        """获取特征表元数据信息

        参数:
            name: 特征表名称
            spark_client: Spark客户端

        返回:
            FeatureTable对象

        异常:
            ValueError: 当表不存在或获取失败时抛出
        """

        # 表名校验
        common_utils.validate_table_name(name)
        common_utils.validate_database(database_name)

        # 构建完整表名
        table_name = common_utils.build_full_table_name(name, database_name)

        try:
            return spark_client.get_feature_table(table_name)
        except Exception as e:
            raise ValueError(f"Failed to get metadata for table '{name}': {str(e)}") from e

    def alter_table_tag(
            self,
            name: str,
            properties: Dict[str, str],
            database_name: Optional[str] = None,
    ):
        """修改表的TBLPROPERTIES属性（有则修改，无则新增）

        Args:
            name: 表名（格式：<table>）
            properties: 要修改/新增的属性字典
            database_name: 特征库名称

        Raises:
            ValueError: 当表不存在或参数无效时抛出
            RuntimeError: 当修改操作失败时抛出

        示例:
            # 修改表属性
            client.alter_tables_tag("user_features", {
                "comment": "更新后的描述",
                "owner": "data_team"
            })
        """
        # 参数校验
        if not properties:
            raise ValueError("properties must be a non-empty dictionary")

        # 表名校验
        common_utils.validate_table_name(name)
        common_utils.validate_database(database_name)

        # 构建完整表名
        table_name = common_utils.build_full_table_name(name, database_name)

        try:
            # 检查表是否存在
            if not self._spark.catalog.tableExists(table_name):
                raise ValueError(f"table '{name}' not exists")

            # 构建属性设置语句
            props_str = ", ".join(
                f"'{k}'='{self._escape_sql_value(v)}'"
                for k, v in properties.items()
            )

            alter_sql = f"ALTER TABLE {table_name} SET TBLPROPERTIES ({props_str})"

            # 执行修改
            self._spark.sql(alter_sql)
            print(f"Successfully updated properties for table '{name}': {list(properties.keys())}")

        except ValueError as e:
            raise  # 直接抛出已知的ValueError
        except Exception as e:
            raise RuntimeError(f"Failed to modify properties for table '{name}': {str(e)}") from e

