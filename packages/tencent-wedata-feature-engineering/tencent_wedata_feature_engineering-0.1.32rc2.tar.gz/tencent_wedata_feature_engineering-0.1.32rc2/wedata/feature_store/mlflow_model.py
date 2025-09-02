import json
from typing import Optional, Dict, Any
import mlflow
import os

class _FeatureStoreModelWrapper(mlflow.pyfunc.PythonModel):
    def __init__(self, model):
        self.model = model

    def predict(self, context, model_input):
       return self.model.predict(model_input)

# def _load_pyfunc(path):
#     # Path provided by mlflow is subdirectory of path needed by score_batch
#     artifact_path = os.path.join(mlflow.pyfunc.DATA, "feature_store")
#     index = path.find(artifact_path)
#     return _FeatureStoreModelWrapper(path[:index])