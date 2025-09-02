from wedata.feature_store.common.protos import feature_store_pb2
class SourceDataColumnInfo:
    def __init__(self, name: str):
        if not name:
            raise ValueError("name must be non-empty.")
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def output_name(self) -> str:
        """
        This field does not exist in the proto, and is provided for convenience.
        """
        return self._name

    @classmethod
    def from_proto(cls, source_data_column_info_proto):
        return cls(name=source_data_column_info_proto.name)

    def to_proto(self):
        return feature_store_pb2.SourceDataColumnInfo(name=self._name)
