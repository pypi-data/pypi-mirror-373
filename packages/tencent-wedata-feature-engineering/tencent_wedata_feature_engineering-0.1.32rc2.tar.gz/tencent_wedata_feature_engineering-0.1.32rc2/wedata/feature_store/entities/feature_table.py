from typing import Dict


class FeatureTable:
    """
    特征表实体类
    """

    def __init__(
        self,
        name,
        table_id,
        description,
        primary_keys,
        partition_columns,
        features,
        creation_timestamp=None,
        online_stores=None,
        notebook_producers=None,
        job_producers=None,
        table_data_sources=None,
        path_data_sources=None,
        custom_data_sources=None,
        timestamp_keys=None,
        tags=None,
    ):
        """Initialize a FeatureTable object."""
        """初始化特征表对象
        
        :param name: 表名
        :param table_id: 表ID
        :param description: 描述
        :param primary_keys: 主键列表
        :param partition_columns: 分区列列表
        :param features: 特征列列表
        :param creation_timestamp: 创建时间戳(可选)
        :param online_stores: 在线存储配置(可选)
        :param notebook_producers: Notebook生产者列表(可选)
        :param job_producers: 作业生产者列表(可选)
        :param table_data_sources: 表数据源列表(可选)
        :param path_data_sources: 路径数据源列表(可选)
        :param custom_data_sources: 自定义数据源列表(可选)
        :param timestamp_keys: 时间戳键列表(可选)
        :param tags: 标签字典(可选)
        """
        self.name = name
        self.table_id = table_id
        self.description = description
        self.primary_keys = primary_keys
        self.partition_columns = partition_columns
        self.features = features
        self.creation_timestamp = creation_timestamp
        self.online_stores = online_stores if online_stores is not None else []
        self.notebook_producers = (
            notebook_producers if notebook_producers is not None else []
        )
        self.job_producers = job_producers if job_producers is not None else []
        self.table_data_sources = (
            table_data_sources if table_data_sources is not None else []
        )
        self.path_data_sources = (
            path_data_sources if path_data_sources is not None else []
        )
        self.custom_data_sources = (
            custom_data_sources if custom_data_sources is not None else []
        )
        self.timestamp_keys = timestamp_keys if timestamp_keys is not None else []
        self._tags = tags

    def __str__(self):
        """
        返回特征表实例的字符串表示，包含所有关键属性信息

        返回:
            格式化的字符串，包含表名、ID、描述、主键、分区列、特征数量、
            时间戳键、创建时间、数据源数量和标签数量等信息
        """
        return (
            f"FeatureTable(\n"
            f"  name='{self.name}',\n"
            f"  table_id='{self.table_id}',\n"
            f"  description='{self.description[:50]}{'...' if len(self.description) > 50 else ''}',\n"
            f"  primary_keys={self.primary_keys},\n"
            f"  partition_columns={self.partition_columns},\n"
            f"  features={len(self.features)},\n"
            f"  timestamp_keys={self.timestamp_keys},\n"
            f"  creation_timestamp={self.creation_timestamp},\n"
            f"  data_sources=[table:{len(self.table_data_sources)} "
            f"path:{len(self.path_data_sources)} custom:{len(self.custom_data_sources)}],\n"
            f"  tags={len(self.tags) if self._tags else 0}\n"
            f")"
        )

    @property
    def tags(self) -> Dict[str, str]:
        """
        Get the tags associated with the feature table.

        :return a Dictionary of all tags associated with the feature table as key/value pairs
        """
        if self._tags is None:
            # If no tags are set, self._tags is expected an empty dictionary.
            raise ValueError(
                "Internal error: tags have not been fetched for this FeatureTable instance"
            )
        return self._tags

