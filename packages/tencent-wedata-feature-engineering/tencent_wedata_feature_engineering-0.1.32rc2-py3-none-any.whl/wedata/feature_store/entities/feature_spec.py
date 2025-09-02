import importlib.metadata
import os
from typing import Any, Dict, List, Type, Union

import mlflow

from google.protobuf.json_format import MessageToDict, ParseDict
from mlflow.utils.file_utils import TempDir, read_yaml, write_yaml

from wedata.feature_store.common.protos import feature_store_pb2
from wedata.feature_store.entities.column_info import ColumnInfo
from wedata.feature_store.entities.feature_column_info import FeatureColumnInfo
from wedata.feature_store.entities.function_info import FunctionInfo
from wedata.feature_store.entities.feature_spec_constants import (
    BOUND_TO,
    DATA_TYPE,
    FEATURE_COLUMN_INFO,
    FEATURE_STORE,
    INCLUDE,
    INPUT_BINDINGS,
    INPUT_COLUMNS,
    INPUT_FUNCTIONS,
    INPUT_TABLES,
    NAME,
    ON_DEMAND_COLUMN_INFO,
    ON_DEMAND_FEATURE,
    OUTPUT_NAME,
    PARAMETER,
    SERIALIZATION_VERSION,
    SOURCE,
    SOURCE_DATA_COLUMN_INFO,
    TABLE_NAME,
    TOPOLOGICAL_ORDERING,
    TRAINING_DATA,
    UDF_NAME,
)
from wedata.feature_store.entities.feature_table_info import FeatureTableInfo
from wedata.feature_store.entities.on_demand_column_info import OnDemandColumnInfo
from wedata.feature_store.entities.source_data_column_info import SourceDataColumnInfo
from wedata.feature_store.utils import common_utils

# Change log for serialization version. Please update for each serialization version.
# 1. Initial.
# 2. (2021/06/16): Record feature_store_client_version to help us make backward compatible changes in the future.
# 3. (2021/08/25): Record table_id to handle feature table lineage stability if tables are deleted.
# 4. (2021/09/25): Record timestamp_lookup_key to handle point-in-time lookups.
# 5. (2021/02/15): Record include flag for column info if False.
#                  Record input functions as FunctionInfo and function computation as OnDemandColumnInfo.
#                  Remove redundant fields: table_name from table_infos, output_name from column_infos.
# 6. (2023/04/21): Record lookback_window in table info for point-in-time lookups.
# 7. (2023/05/05): Record the Spark data type for all columns to track model signatures.
# 8. (2023/08/14): Record the topological_ordering for all columns to support chained transform and lookup.
# 9. (2023/09/11): Change the type of lookback_window from int to double for sub-second values


class FeatureSpec:

    FEATURE_ARTIFACT_FILE = "feature_spec.yaml"
    SERIALIZATION_VERSION_NUMBER = 9

    def __init__(
        self,
        column_infos: List[ColumnInfo],
        table_infos: List[FeatureTableInfo],
        function_infos: List[FunctionInfo],
        workspace_id: int = None,
        feature_store_client_version: str = None,
        serialization_version: int = None,
    ):
        self._column_infos = column_infos
        self._table_infos = table_infos
        self._function_infos = function_infos
        self._workspace_id = workspace_id
        if self._workspace_id is None:
            self._workspace_id = 0
        # The Feature Store Python client version which wrote this FeatureSpec.
        # If empty, the client version is <=0.3.1.
        self._feature_store_client_version = feature_store_client_version
        if self._feature_store_client_version is None:
            try:
                self._feature_store_client_version = importlib.metadata.version("tencent_wedata_feature_engineering")
            except importlib.metadata.PackageNotFoundError:
                self._feature_store_client_version = "unknown"  # 或其它默认值
        self._serialization_version = serialization_version

        # Perform validations
        self._validate_column_infos()
        self._validate_table_infos()
        self._validate_function_infos()

    def _validate_column_infos(self):
        if not self.column_infos:
            raise ValueError("column_infos must be non-empty.")

        for column_info in self.column_infos:
            if not isinstance(column_info, ColumnInfo):
                raise ValueError(
                    f"Expected all elements of column_infos to be instances of ColumnInfo. "
                    f"'{column_info}' is of the wrong type."
                )
            if (
                self._serialization_version >= 8
                and column_info.topological_ordering is not None
            ):
                ordering = column_info.topological_ordering
                if not isinstance(ordering, int) or ordering < 0:
                    raise ValueError(
                        "The topological_ordering of column_info must be non non-negative integers."
                    )

    def _validate_table_infos(self):
        if self.table_infos is None:
            raise ValueError("Internal Error: table_infos must be provided.")

        # table_infos should not be duplicated
        common_utils.validate_strings_unique(
            [table_info.table_name for table_info in self.table_infos],
            "Internal Error: Expect all table_names in table_infos to be unique. Found duplicates {}",
        )

        # Starting FeatureSpec v3, unique table names in table_infos must match those in column_infos.
        if self.serialization_version >= 3:
            unique_table_names = set(
                [table_info.table_name for table_info in self.table_infos]
            )
            unique_column_table_names = set(
                [fci.table_name for fci in self.feature_column_infos]
            )
            if unique_table_names != unique_column_table_names:
                raise Exception(
                    f"Internal Error: table_names from table_infos {sorted(unique_table_names)} "
                    f"must match those from column_infos {sorted(unique_column_table_names)}"
                )

    def _validate_function_infos(self):
        if self.function_infos is None:
            raise ValueError("Internal Error: function_infos must be provided.")

        # function_infos should not be duplicated
        common_utils.validate_strings_unique(
            [function_info.udf_name for function_info in self.function_infos],
            "Internal Error: Expect all udf_names in function_infos to be unique. Found duplicates {}",
        )

        # Unique UDF names in function_infos must match those in column_infos.
        # No version check is required as both fields were added simultaneously in FeatureSpec v5.
        unique_udf_names = set(
            [function_info.udf_name for function_info in self.function_infos]
        )
        unique_column_udf_names = set(
            [odci.udf_name for odci in self.on_demand_column_infos]
        )
        if unique_udf_names != unique_column_udf_names:
            raise Exception(
                f"Internal Error: udf_names from function_infos {sorted(unique_udf_names)} "
                f"must match those from column_infos {sorted(unique_column_udf_names)}"
            )

    @property
    def column_infos(self):
        return self._column_infos

    @property
    def table_infos(self):
        return self._table_infos

    @property
    def function_infos(self):
        return self._function_infos

    @property
    def workspace_id(self):
        return self._workspace_id
    @property
    def source_data_column_infos(self) -> List[SourceDataColumnInfo]:
        return self._get_infos_of_type(SourceDataColumnInfo)
    @property
    def feature_column_infos(self) -> List[FeatureColumnInfo]:
        return self._get_infos_of_type(FeatureColumnInfo)

    @property
    def on_demand_column_infos(self) -> List[OnDemandColumnInfo]:
        return self._get_infos_of_type(OnDemandColumnInfo)

    @property
    def serialization_version(self) -> int:
        return self._serialization_version

    def _get_infos_of_type(
            self,
            info_type: Union[
                Type[SourceDataColumnInfo],
                Type[FeatureColumnInfo],
                Type[OnDemandColumnInfo],
            ],
    ):
        """
        Helper method to return the ColumnInfo.info subinfo field based on its type.
        """
        return [
            column_info.info
            for column_info in self.column_infos
            if isinstance(column_info.info, info_type)
        ]

    @classmethod
    def from_proto(cls, feature_spec_proto):
        # Serialization version is not deserialized from the proto as there is currently only one
        # possible version.
        # print(f"feature_spec_proto:{feature_spec_proto}")
        column_infos = [
            ColumnInfo.from_proto(column_info_proto)
            for column_info_proto in feature_spec_proto.input_columns
        ]
        # print(f"column_infos:{column_infos}")

        table_infos = [
            FeatureTableInfo.from_proto(table_info_proto)
            for table_info_proto in feature_spec_proto.input_tables
        ]
        # print(f"table_infos:{table_infos}")
        # 本期不支持 udf_function
        function_infos = [
            FunctionInfo.from_proto(function_info_proto)
            for function_info_proto in feature_spec_proto.input_functions
        ]
        return cls(
            column_infos=column_infos,
            table_infos=table_infos,
            function_infos=function_infos,
            workspace_id=feature_spec_proto.workspace_id,
            feature_store_client_version=feature_spec_proto.feature_store_client_version,
            serialization_version=feature_spec_proto.serialization_version,
        )


    @staticmethod
    def _input_columns_proto_to_yaml_dict(column_info: Dict[str, Any]):
        """
        Converts a single ColumnInfo's proto dict to the expected element in FeatureSpec YAML's input_columns.
        To keep the YAML clean, unnecessary fields are removed (e.g. SourceDataColumnInfo.name field, ColumnInfo.include when True).

        Example of a column_info transformation. Note that "name" and "include" attributes were excluded.
        {"source_data_column_info": {"name": "source_column"}, "include": True} -> {"source_column": {"source": "training_data"}}

        Order of elements in the YAML dict should be:
        1. Attributes present in ColumnInfo.info, using the proto field order
        2. Remaining attributes of ColumnInfo, using the proto field order
        3. Feature Store source type
        """
        # Parse oneof field ColumnInfo.info level attributes as column_info_attributes; record column_name, source
        if SOURCE_DATA_COLUMN_INFO in column_info:
            column_info_attributes = column_info[SOURCE_DATA_COLUMN_INFO]
            # pop NAME attribute and use as the YAML key for this column_info to avoid redundancy in YAML
            column_name, source = column_info_attributes.pop(NAME), TRAINING_DATA
        elif FEATURE_COLUMN_INFO in column_info:
            column_info_attributes = column_info[FEATURE_COLUMN_INFO]
            # pop OUTPUT_NAME attribute and use as the YAML key for this column_info to avoid redundancy in YAML
            column_name, source = column_info_attributes.pop(OUTPUT_NAME), FEATURE_STORE
        elif ON_DEMAND_COLUMN_INFO in column_info:
            column_info_attributes = column_info[ON_DEMAND_COLUMN_INFO]
            # Map InputBindings message dictionary to {parameter: bound_to} KV dictionary if defined
            if INPUT_BINDINGS in column_info_attributes:
                column_info_attributes[INPUT_BINDINGS] = {
                    ib[PARAMETER]: ib[BOUND_TO]
                    for ib in column_info_attributes[INPUT_BINDINGS]
                }
            # pop OUTPUT_NAME attribute and use as the YAML key for this column_info to avoid redundancy in YAML
            column_name, source = (
                column_info_attributes.pop(OUTPUT_NAME),
                ON_DEMAND_FEATURE,
            )
        else:
            raise ValueError(
                f"Expected column_info to be keyed by a valid ColumnInfo.info type. "
                f"'{column_info}' has key '{list(column_info)[0]}'."
            )

        # Parse and insert ColumnInfo level attributes
        # Note: the ordering of fields in the result yaml file is undefined but in reality, they are
        # in the same order as they are added in the column_info_attributes dict.

        # DATA_TYPE is supported starting FeatureSpec v7 and is not guaranteed to exist.
        if DATA_TYPE in column_info:
            column_info_attributes[DATA_TYPE] = column_info[DATA_TYPE]
        if not column_info.get(INCLUDE, False):
            column_info_attributes[INCLUDE] = False
        else:
            column_info_attributes[INCLUDE] = True
        # TOPOLOGICAL_ORDERING is supported starting FeatureSpec v8.
        if TOPOLOGICAL_ORDERING in column_info:
            column_info_attributes[TOPOLOGICAL_ORDERING] = column_info[
                TOPOLOGICAL_ORDERING
            ]

        # Insert source; return YAML keyed by column_name
        column_info_attributes[SOURCE] = source
        return {column_name: column_info_attributes}

    def _to_dict(self):
        """
        Convert FeatureSpec to a writeable YAML artifact. Uses MessageToDict to convert FeatureSpec proto to dict.
        Sanitizes and modifies the dict as follows:
        1. Remove redundant or unnecessary information for cleanliness in the YAML
        2. Modifies the dict to be of the format {column_name: column_attributes_dict}

        :return: Sanitized FeatureSpec dictionary of {column_name: column_attributes}
        """
        yaml_dict = MessageToDict(self.to_proto(), preserving_proto_field_name=True)
        yaml_dict[INPUT_COLUMNS] = [
            self._input_columns_proto_to_yaml_dict(column_info)
            for column_info in yaml_dict[INPUT_COLUMNS]
        ]

        if INPUT_TABLES in yaml_dict:
            # pop TABLE_NAME attribute and use as the YAML key for each table_info to avoid redundancy in YAML
            yaml_dict[INPUT_TABLES] = [
                {table_info.pop(TABLE_NAME): table_info}
                for table_info in yaml_dict[INPUT_TABLES]
            ]
        if INPUT_FUNCTIONS in yaml_dict:
            # pop UDF_NAME attribute and use as the YAML key for each table_info to avoid redundancy in YAML
            yaml_dict[INPUT_FUNCTIONS] = [
                {function_info.pop(UDF_NAME): function_info}
                for function_info in yaml_dict[INPUT_FUNCTIONS]
            ]

        # For readability, place SERIALIZATION_VERSION last in the dictionary.
        yaml_dict[SERIALIZATION_VERSION] = yaml_dict.pop(SERIALIZATION_VERSION)
        return yaml_dict

    def save(self, path: str):
        """
        Convert spec to a YAML artifact and store at given `path` location.
        :param path: Root path to where YAML artifact is expected to be stored.
        :return: None
        """
        write_yaml(
            root=path,
            file_name=self.FEATURE_ARTIFACT_FILE,
            data=self._to_dict(),
            sort_keys=False,
        )

    @staticmethod
    def _input_columns_yaml_to_proto_dict(column_info: Dict[str, Any]):
        """
        Convert the FeatureSpec YAML dictionary to the expected ColumnInfo proto dictionary.

        Example of a column_info transformation.
        {"source_column": {"source": "training_data"}} -> {"source_data_column_info": {"name": "source_column"}}
        """
        if len(column_info) != 1:
            raise ValueError(
                f"Expected column_info dictionary to only have one key, value pair. "
                f"'{column_info}' has length {len(column_info)}."
            )
        column_name, column_data = list(column_info.items())[0]
        if not column_data:
            raise ValueError(
                f"Expected values of '{column_name}' dictionary to be non-empty."
            )
        if SOURCE not in column_data:
            raise ValueError(
                f"Expected values of column_info dictionary to include the source. No source found "
                f"for '{column_name}'."
            )

        # Parse oneof field ColumnInfo.info level attributes
        source = column_data.pop(SOURCE)
        if source == TRAINING_DATA:
            column_data[NAME] = column_name
            column_info_dict = {SOURCE_DATA_COLUMN_INFO: column_data}
        elif source == FEATURE_STORE:
            column_data[OUTPUT_NAME] = column_name
            column_info_dict = {FEATURE_COLUMN_INFO: column_data}
        elif source == ON_DEMAND_FEATURE:
            column_data[OUTPUT_NAME] = column_name
            # Map {parameter_val: bound_to_val} dictionary to InputBindings(parameter, bound_to) message dictionary.
            column_data[INPUT_BINDINGS] = [
                {PARAMETER: parameter, BOUND_TO: bound_to}
                for parameter, bound_to in column_data.get(INPUT_BINDINGS, {}).items()
            ]
            column_info_dict = {ON_DEMAND_COLUMN_INFO: column_data}
        else:
            raise ValueError(
                f"Internal Error: Expected column_info to have source matching oneof ColumnInfo.info. "
                f"'{column_info}' has source of '{source}'."
            )

        # Parse ColumnInfo level attributes
        # TOPOLOGICAL_ORDERING is supported starting FeatureSpec v8.
        if TOPOLOGICAL_ORDERING in column_data:
            column_info_dict[TOPOLOGICAL_ORDERING] = column_data.pop(
                TOPOLOGICAL_ORDERING
            )
        # DATA_TYPE is supported starting FeatureSpec v7 and is not guaranteed to exist.
        if DATA_TYPE in column_data:
            column_info_dict[DATA_TYPE] = column_data.pop(DATA_TYPE)
        # INCLUDE is supported starting FeatureSpec v5 and only present in the YAML when INCLUDE = False
        if INCLUDE in column_data:
            column_info_dict[INCLUDE] = column_data.pop(INCLUDE)
        return column_info_dict

    @classmethod
    def _from_dict(cls, spec_dict):
        """
        Convert YAML artifact to FeatureSpec. Transforms YAML artifact to dict keyed by
        source_data_column_info or feature_column_info, such that ParseDict can convert the dict to
        a proto message, and from_proto can convert the proto message to a FeatureSpec object
        :return: :py:class:`~databricks.ml_features_common.entities.feature_spec.FeatureSpec`
        """
        if INPUT_COLUMNS not in spec_dict:
            raise ValueError(
                f"{INPUT_COLUMNS} must be a key in {cls.FEATURE_ARTIFACT_FILE}."
            )
        if not spec_dict[INPUT_COLUMNS]:
            raise ValueError(
                f"{INPUT_COLUMNS} in {cls.FEATURE_ARTIFACT_FILE} must be non-empty."
            )
        spec_dict[INPUT_COLUMNS] = [
            cls._input_columns_yaml_to_proto_dict(column_info)
            for column_info in spec_dict[INPUT_COLUMNS]
        ]

        # feature_spec.yaml doesn't include input_tables, input_functions if any are true:
        # 1. The YAML is written by an older client that does not support the functionality.
        # 2. The FeatureSpec does not contain FeatureLookups (input_tables), FeatureFunctions (input_functions).
        input_tables = []
        for input_table in spec_dict.get(INPUT_TABLES, []):
            table_name, attributes = list(input_table.items())[0]
            input_tables.append({TABLE_NAME: table_name, **attributes})
        spec_dict[INPUT_TABLES] = input_tables

        input_functions = []
        for input_function in spec_dict.get(INPUT_FUNCTIONS, []):
            udf_name, attributes = list(input_function.items())[0]
            input_functions.append({UDF_NAME: udf_name, **attributes})
        spec_dict[INPUT_FUNCTIONS] = input_functions

        print(f"spec_dict:{spec_dict}")
        return cls.from_proto(
            ParseDict(spec_dict, feature_store_pb2.FeatureSpec(), ignore_unknown_fields=True)
        )

    @classmethod
    def _read_file(cls, path: str):
        """
        Read the YAML artifact from a file path.
        """
        parent_dir, file = os.path.split(path)
        spec_dict = read_yaml(parent_dir, file)
        return cls._from_dict(spec_dict)

    @classmethod
    def load(cls, path: str):
        """
        Load the FeatureSpec YAML artifact in the provided root directory (at path/feature_spec.yaml).

        :param path: Root path to the YAML artifact. This can be a MLflow artifact path or file path.
        :return: :py:class:`~databricks.ml_features_common.entities.feature_spec.FeatureSpec`
        """
        # Create the full file path to the FeatureSpec.
        path = os.path.join(path, cls.FEATURE_ARTIFACT_FILE)

        if common_utils.is_artifact_uri(path):
            with TempDir() as tmp_location:
                # Returns a file and not directory since the artifact_uri is a single file.
                local_path = mlflow.artifacts.download_artifacts(
                    artifact_uri=path, dst_path=tmp_location.path()
                )
                return FeatureSpec._read_file(local_path)
        else:
            return FeatureSpec._read_file(path)

    def to_proto(self):
        proto_feature_spec = feature_store_pb2.FeatureSpec()
        for column_info in self.column_infos:
            proto_feature_spec.input_columns.append(column_info.to_proto())
        for table_info in self.table_infos:
            proto_feature_spec.input_tables.append(table_info.to_proto())
        for function_info in self.function_infos:
            proto_feature_spec.input_functions.append(function_info.to_proto())
        proto_feature_spec.serialization_version = self.serialization_version
        proto_feature_spec.workspace_id = self.workspace_id
        proto_feature_spec.feature_store_client_version = (
            self._feature_store_client_version
        )
        return proto_feature_spec
