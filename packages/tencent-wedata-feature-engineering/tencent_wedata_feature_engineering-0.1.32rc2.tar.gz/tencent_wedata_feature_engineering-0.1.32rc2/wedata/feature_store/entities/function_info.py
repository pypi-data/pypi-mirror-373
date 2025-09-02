from collections import defaultdict
from typing import List, Optional

from pyspark.sql import Column, DataFrame
from pyspark.sql.functions import isnull, when
from pyspark.sql.types import StringType, StructField, StructType
from wedata.feature_store.common.protos import feature_store_pb2

class FunctionParameterInfo():
    def __init__(self, name: str, type_text: str):
        self._name = name
        self._type_text = type_text

    @property
    def name(self) -> str:
        return self._name

    @property
    def type_text(self) -> str:
        return self._type_text

    @classmethod
    def from_dict(cls, function_parameter_info_json):
        return FunctionParameterInfo(
            function_parameter_info_json["name"],
            function_parameter_info_json["type_text"],
        )


class FunctionInfo():
    """
    Helper entity class that exposes properties in GetFunction's response JSON as attributes.
    https://docs.databricks.com/api-explorer/workspace/functions/get

    Note: empty fields (e.g. when 0 input parameters) are not included in the response JSON.
    """

    # Python UDFs have external_language = "Python"
    PYTHON = "Python"

    def __init__(
        self,
        full_name: str,
        input_params: List[FunctionParameterInfo],
        routine_definition: Optional[str],
        external_language: Optional[str],
    ):
        self._full_name = full_name
        self._input_params = input_params
        self._routine_definition = routine_definition
        self._external_language = external_language


    @property
    def full_name(self) -> str:
        return self._full_name

    @property
    def input_params(self) -> List[FunctionParameterInfo]:
        return self._input_params

    @property
    def routine_definition(self) -> Optional[str]:
        return self._routine_definition

    @property
    def external_language(self) -> Optional[str]:
        """
        Field is None if language is SQL (not an external language).
        """
        return self._external_language

    @classmethod
    def from_dict(cls, function_info_json):
        input_params = function_info_json.get("input_params", {}).get("parameters", [])
        return FunctionInfo(
            full_name=function_info_json["full_name"],
            input_params=[FunctionParameterInfo.from_dict(p) for p in input_params],
            routine_definition=function_info_json.get("routine_definition", None),
            external_language=function_info_json.get("external_language", None),
        )

    @classmethod
    def from_proto(cls, function_info_proto):
        return cls(full_name=function_info_proto.udf_name)

    def to_proto(self):
        return feature_store_pb2.FunctionInfo(
            full_name=self.full_name,
            input_params=self.input_params,
            routine_definition=self.routine_definition,
            external_language=self.external_language
        )
