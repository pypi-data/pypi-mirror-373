
OVERWRITE = "overwrite"
APPEND = "append"
PATH = "path"
TABLE = "table"
CUSTOM = "custom"
PREDICTION_COLUMN_NAME = "prediction"
MODEL_DATA_PATH_ROOT = "feature_store"
RAW_MODEL_FOLDER = "raw_model"
UTF8_BYTES_PER_CHAR = 4
MAX_PRIMARY_KEY_STRING_LENGTH_CHARS = 100
MAX_PRIMARY_KEY_STRING_LENGTH_BYTES = (
    MAX_PRIMARY_KEY_STRING_LENGTH_CHARS * UTF8_BYTES_PER_CHAR
)
STREAMING_TRIGGER_CONTINUOUS = "continuous"
STREAMING_TRIGGER_ONCE = "once"
STREAMING_TRIGGER_PROCESSING_TIME = "processingTime"
DEFAULT_WRITE_STREAM_TRIGGER = {STREAMING_TRIGGER_PROCESSING_TIME: "5 seconds"}
_DEFAULT_PUBLISH_STREAM_TRIGGER = {STREAMING_TRIGGER_PROCESSING_TIME: "5 minutes"}
FEATURE_STORE_CLIENT = "FeatureStoreClient"


_WARN = "WARN"
_ERROR = "ERROR"
_SOURCE_FORMAT_DELTA = "delta"

_NO_RESULT_TYPE_PASSED = "NO_RESULT_TYPE"
_USE_SPARK_NATIVE_JOIN = "use_spark_native_join"
_PREBUILT_ENV_URI = "prebuilt_env_uri"

# MLflow模型相关常量(原mlflow_model_constants.py)
# Module name of the original mlflow_model
MLFLOW_MODEL_NAME = "wedata.feature_store.mlflow_model"

# FeatureStoreClient.log_model将记录包含'raw_model'文件夹的模型
# 该文件夹存储原始模型的MLmodel文件，用于推理
RAW_MODEL_FOLDER = "raw_model"

# ML模型文件名常量
ML_MODEL = "MLmodel"

# 特征查找客户端的PyPI包名
FEATURE_LOOKUP_CLIENT_PIP_PACKAGE = "tencent-wedata-feature-engineering"

# 特征查找版本号
FEATURE_LOOKUP_CLIENT_MAJOR_VERSION = "0.1.32rc2"

# 特征存储内部数据目录
FEATURE_STORE_INTERNAL_DATA_DIR = "_wedata_internal/"
WEDATA_DEFAULT_FEATURE_STORE_DATABASE = "WEDATA_DEFAULT_FEATURE_STORE_DATABASE"

# 特征表属性
FEATURE_TABLE_KEY = "wedata.feature_table"
FEATURE_TABLE_VALUE = "true"

FEATURE_TABLE_PROJECT = "wedata.feature_project_id"