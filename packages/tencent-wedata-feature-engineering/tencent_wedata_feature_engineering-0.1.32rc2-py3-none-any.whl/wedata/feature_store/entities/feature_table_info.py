from typing import Optional


from wedata.feature_store.common.protos import feature_store_pb2

class FeatureTableInfo:
    def __init__(
        self, table_name: str, table_id: str, lookback_window: Optional[float] = None
    ):
        if not table_name:
            raise ValueError("table_name must be non-empty.")
        if not table_id:
            raise ValueError("table_id must be non-empty.")
        self._table_name = table_name
        self._table_id = table_id
        self._lookback_window = lookback_window

    @property
    def table_name(self):
        return self._table_name

    @property
    def table_id(self):
        return self._table_id

    @property
    def lookback_window(self):
        return self._lookback_window

    @classmethod
    def from_proto(cls, feature_table_info_proto):
        lookback_window = feature_table_info_proto.lookback_window or None
        # lookback_window = (
        #     feature_table_info_proto.lookback_window
        #     if feature_table_info_proto.lookback_window != 0
        #     else None
        # )
        return cls(
            table_name=feature_table_info_proto.table_name,
            table_id=feature_table_info_proto.table_id,
            lookback_window=lookback_window,
        )

    def to_proto(self):
        return feature_store_pb2.FeatureTableInfo(
            table_name=self.table_name,
            table_id=self.table_id,
            lookback_window=self.lookback_window,
        )
