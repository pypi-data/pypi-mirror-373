# This is a test script for FeatureStoreClient
import os
from datetime import date
from typing import Optional, Dict

import pandas as pd
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col
from sklearn.ensemble import RandomForestClassifier

import mlflow.sklearn

from wedata.feature_store.client import FeatureStoreClient
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, IntegerType, DoubleType, DateType

from wedata.feature_store.entities.feature_lookup import FeatureLookup
from wedata.feature_store.entities.training_set import TrainingSet
from wedata.feature_store.utils import common_utils


# 创建FeatureStoreClient实例
def create_client() -> FeatureStoreClient:
    spark = SparkSession.builder \
        .appName("FeatureStoreDemo") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.jars.packages", "io.delta:delta-core_2.12:2.4.0") \
        .enableHiveSupport() \
        .getOrCreate()

    print(spark.catalog.currentCatalog())

    # 创建FeatureStoreClient实例
    client = FeatureStoreClient(spark)
    return client

# 创建特征表
def create_table(client: FeatureStoreClient):
    user_data = [
        (1001, 25, "F", 120.5, date(2020, 5, 15)),  # user_id, age, gender, avg_purchase, member_since
        (1002, 30, "M", 200.0, date(2019, 3, 10)),
        (1003, 35, "F", 180.3, date(2021, 1, 20))
    ]

    # 定义schema
    user_schema = StructType([
        StructField("user_id", IntegerType(), False, metadata={"comment": "用户唯一标识ID"}),
        StructField("age", IntegerType(), True, metadata={"comment": "用户年龄"}),
        StructField("gender", StringType(), True, metadata={"comment": "用户性别(F-女性,M-男性)"}),
        StructField("avg_purchase", DoubleType(), True, metadata={"comment": "用户平均消费金额"}),
        StructField("member_since", DateType(), True, metadata={"comment": "用户注册日期"})
    ])

    # 创建DataFrame
    user_df = client.spark.createDataFrame(user_data, user_schema)

    display(user_df)

    client.create_table(
        name="user_features",  # 表名
        primary_keys=["user_id"],      # 主键
        df=user_df,                   # 数据
        partition_columns=["member_since"],  # 按注册日期分区
        description="用户基本特征和消费行为特征",  # 描述
        tags={  # 业务标签
            "create_by": "tencent",
            "sensitivity": "internal"
        }
    )

    # 商品数据样例
    product_data = [
        (5001, "电子", 599.0, 0.85, date(2024, 1, 1)),
        (5002, "服装", 199.0, 0.92, date(2023, 11, 15)),
        (5003, "家居", 299.0, 0.78, date(2024, 2, 20))
    ]

    # 定义schema
    product_schema = StructType([
        StructField("product_id", IntegerType(), False),
        StructField("category", StringType(), True),
        StructField("price", DoubleType(), True),
        StructField("popularity", DoubleType(), True),
        StructField("release_date", DateType(), True)
    ])

    # 创建DataFrame
    product_df = client.spark.createDataFrame(product_data, product_schema)


    display(product_df)

    # 创建商品特征表
    client.create_table(
        name="product_features",
        primary_keys=["product_id"],
        df=product_df,
        description="商品基本属性和受欢迎程度",
        tags={  # 业务标签
            "feature_table": "true",
            "sensitivity": "internal"
        }
    )


# 追加写入数据
def append_data(client: FeatureStoreClient):
    user_data = [
        (1004, 45, "F", 120.5, date(2020, 5, 15)),
        (1005, 55, "M", 200.0, date(2019, 3, 10)),
        (1006, 65, "F", 180.3, date(2021, 1, 20))
    ]

    user_schema = StructType([
        StructField("user_id", IntegerType(), False, metadata={"comment": "用户唯一标识ID"}),
        StructField("age", IntegerType(), True, metadata={"comment": "用户年龄"}),
        StructField("gender", StringType(), True, metadata={"comment": "用户性别(F-女性,M-男性)"}),
        StructField("avg_purchase", DoubleType(), True, metadata={"comment": "用户平均消费金额"}),
        StructField("member_since", DateType(), True, metadata={"comment": "用户注册日期"})
    ])

    user_df = client.spark.createDataFrame(user_data, user_schema)

    display(user_df)

    client.write_table(
        name="user_features",
        df=user_df,
        mode="append"
    )

    product_data = [
        (5007, "食品", 599.0, 0.85, date(2024, 1, 1)),
        (5008, "玩具", 199.0, 0.92, date(2023, 11, 15)),
        (5009, "电脑", 299.0, 0.78, date(2024, 2, 20))
    ]

    product_schema = StructType([
        StructField("product_id", IntegerType(), False, metadata={"comment": "商品唯一标识ID"}),
        StructField("category", StringType(), True, metadata={"comment": "商品类别"}),
        StructField("price", DoubleType(), True, metadata={"comment": "商品价格(元)"}),
        StructField("popularity", DoubleType(), True, metadata={"comment": "商品受欢迎程度(0-1)"}),
        StructField("release_date", DateType(), True, metadata={"comment": "商品发布日期"})
    ])

    product_df = client.spark.createDataFrame(product_data, product_schema)

    display(product_df)

    client.write_table(
        name="product_features",
        df=product_df,
        mode="append"
    )

# 读取特征表数据
def read_table(client: FeatureStoreClient):

    # 读取用户特征表
    user_df = client.read_table("user_features")
    display(user_df)

    # 读取商品特征表
    product_df = client.read_table("product_features")
    display(product_df)

# 获取特征表元数据
def get_table(client: FeatureStoreClient):
    feature_table_user = client.get_table(name="user_features")
    print(feature_table_user)


# 创建训练集
def create_training_set(client: FeatureStoreClient)  -> TrainingSet:

    # 订单数据样例
    order_data = [
        (9001, 1001, 5001, date(2025, 3, 1), 1, 0),
        (9002, 1002, 5002, date(2025, 3, 2), 2, 1),
        (9003, 1003, 5003, date(2025, 3, 3), 1, 0)
    ]

    # 定义schema
    order_schema = StructType([
        StructField("order_id", IntegerType(), False, metadata={"comment": "订单唯一标识ID"}),
        StructField("user_id", IntegerType(), True, metadata={"comment": "用户ID"}),
        StructField("product_id", IntegerType(), True, metadata={"comment": "商品ID"}),
        StructField("order_date", DateType(), True, metadata={"comment": "订单日期"}),
        StructField("quantity", IntegerType(), True, metadata={"comment": "购买数量"}),
        StructField("is_returned", IntegerType(), True, metadata={"comment": "是否退货(0-未退货,1-已退货)"})
    ])

    # 创建DataFrame
    order_df = client.spark.createDataFrame(order_data, order_schema)

    # 查看订单数据
    display(order_df)

    # 定义用户特征查找
    user_feature_lookup = FeatureLookup(
        table_name="user_features",
        feature_names=["age", "gender", "avg_purchase"],  # 选择需要的特征列
        lookup_key="user_id"  # 关联键
    )

    # 定义商品特征查找
    product_feature_lookup = FeatureLookup(
        table_name="product_features",
        feature_names=["category", "price", "popularity"],  # 选择需要的特征列
        lookup_key="product_id"  # 关联键
    )

    # 创建训练集
    training_set = client.create_training_set(
        df=order_df,  # 基础数据
        feature_lookups=[user_feature_lookup, product_feature_lookup],  # 特征查找配置
        label="is_returned",  # 标签列
        exclude_columns=["order_id"]  # 排除不需要的列
    )

    # 获取最终的训练DataFrame
    training_df = training_set.load_df()

    # 查看训练数据
    display(training_df)

    return training_set


# 查看df中数据
def display(df):

    """
    打印DataFrame的结构和数据

    参数:
        df (DataFrame): 要打印的Spark DataFrame
        num_rows (int): 要显示的行数，默认为20
        truncate (bool): 是否截断过长的列，默认为True
    """
    # 打印表结构
    print("=== 表结构 ===")
    df.printSchema()

    # 打印数据
    print("\n=== 数据示例 ===")
    df.show(20, True)

    # 打印行数统计
    print(f"\n总行数: {df.count()}")


def log_model(client: FeatureStoreClient,
              training_set: TrainingSet
              ):

    # 初始化模型
    model = RandomForestClassifier(
        n_estimators=100,  # 增加树的数量提高模型稳定性
        random_state=42    # 固定随机种子保证可复现性
    )

    # 获取训练数据并转换为Pandas格式
    train_pd = training_set.load_df().toPandas()

    # 特征工程处理
    # 1. 处理分类特征
    train_pd['gender'] = train_pd['gender'].map({'F': 0, 'M': 1})
    train_pd = pd.get_dummies(train_pd, columns=['category'])

    # 2. 处理日期特征（转换为距今天数）
    current_date = pd.to_datetime('2025-04-19')  # 使用参考信息中的当前时间
    train_pd['order_days'] = (current_date - pd.to_datetime(train_pd['order_date'])).dt.days
    train_pd = train_pd.drop('order_date', axis=1)

    # 3. 创建交互特征（价格*数量）
    train_pd['total_amount'] = train_pd['price'] * train_pd['quantity']

    # 分离特征和标签
    X = train_pd.drop("is_returned", axis=1)
    y = train_pd["is_returned"]

    # 训练模型
    model.fit(X, y)
    # 记录模型到MLflow
    with mlflow.start_run():
        client.log_model(
            model=model,
            artifact_path="return_prediction_model",  # 更符合业务场景的路径名
            flavor=mlflow.sklearn,
            training_set=training_set,
            registered_model_name="product_return_prediction_model"  # 更准确的模型名称
        )

def log_model(client: FeatureStoreClient,
              training_set: TrainingSet
              ):
    """
    训练并记录商品退货预测模型

    参数:
        client: FeatureStoreClient实例
        training_set: 训练集对象

    返回:
        无
    """
    # 获取数据并转换为Pandas格式
    train_pd = training_set.load_df().toPandas()

    # 仅做最基本的特征处理
    train_pd['gender'] = train_pd['gender'].map({'F': 0, 'M': 1})

    # 分离特征和标签
    X = train_pd[['age', 'gender', 'avg_purchase', 'price', 'popularity']]  # 只使用基本特征
    y = train_pd["is_returned"]

    # 使用默认参数的随机森林
    model = RandomForestClassifier(random_state=42)
    model.fit(X, y)

    # 记录模型
    with mlflow.start_run():
        client.log_model(
            model=model,
            artifact_path="return_prediction_model",  # 业务场景的路径名
            flavor=mlflow.sklearn,
            training_set=training_set,
            registered_model_name="product_return_prediction_model",  # 模型名称
        )

def load_model(client: FeatureStoreClient):
    import mlflow
    import logging
    from pyspark.sql import DataFrame

    # 配置日志
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # 模型URI - 应该从配置或环境变量中获取
    logged_model = 'runs:/7ef2294070824daaadec065e1640211f/return_prediction_model'

    # 加载模型
    logger.info("正在加载MLflow模型...")
    loaded_model = mlflow.pyfunc.load_model(logged_model)

    # 定义测试数据schema
    new_schema = StructType([
        StructField("age", IntegerType(), True, metadata={"comment": "用户年龄"}),
        StructField("gender", StringType(), True, metadata={"comment": "用户性别(F-女性,M-男性)"}),
        StructField("avg_purchase", DoubleType(), True, metadata={"comment": "用户平均消费金额"}),
        #StructField("category", StringType(), True, metadata={"comment": "商品类别"}),
        StructField("price", DoubleType(), True, metadata={"comment": "商品价格(元)"}),
        StructField("popularity", DoubleType(), True, metadata={"comment": "商品受欢迎程度(0-1)"})
    ])

    # 测试数据
    new_data = [
        (21, "M", 100.0, 500.0, 0.5),
        (25, "F", 500.0, 100.0, 0.9),
        (31, "M", 1000.0, 100.0, 0.9)
    ]

    # 创建Spark DataFrame
    p_df = client.spark.createDataFrame(new_data, new_schema)

    # 转换为Pandas DataFrame并进行必要的数据预处理
    pd_df = p_df.toPandas()
    pd_df = pd_df[['age', 'gender', 'avg_purchase', 'price', 'popularity']]
    pd_df['gender'] = pd_df['gender'].map({'F': 0, 'M': 1})

    # 执行预测
    logger.info("正在执行预测...")
    predictions = loaded_model.predict(pd_df)

    print("预测结果:", predictions)
    return predictions



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    client = create_client()
    #create_table(client)
    #append_data(client)
    #read_table(client)
    #get_table(client)
    training_set = create_training_set(client)
    log_model(client, training_set)



