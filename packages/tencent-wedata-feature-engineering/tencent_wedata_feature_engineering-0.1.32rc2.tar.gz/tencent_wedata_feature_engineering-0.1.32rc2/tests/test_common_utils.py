from wedata.feature_store.utils import common_utils

import os
import logging
import mlflow
logging.basicConfig(level=logging.ERROR)

def test_build_full_table_name():
    os.environ["WEDATA_FEATURE_STORE_DATABASE"] = ""
    os.environ["QCLOUD_UIN"] = "test"
    mlflow.sklearn.log_model()
    common_utils.build_full_table_name("test")