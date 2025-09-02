import logging
from dataclasses import dataclass
from functools import reduce
from typing import Dict, List, Set, Tuple, Type, Union

import yaml
from mlflow.utils.file_utils import YamlSafeDumper

from wedata.feature_store.entities.column_info import ColumnInfo
from wedata.feature_store.entities.feature_column_info import FeatureColumnInfo
from wedata.feature_store.entities.feature_spec import FeatureSpec
from wedata.feature_store.entities.on_demand_column_info import OnDemandColumnInfo
from wedata.feature_store.entities.source_data_column_info import SourceDataColumnInfo
from wedata.feature_store.utils.topological_sort import topological_sort

DEFAULT_GRAPH_DEPTH_LIMIT = 5

COLUMN_INFO_TYPE_SOURCE = "SOURCE"
COLUMN_INFO_TYPE_ON_DEMAND = "ON_DEMAND"
COLUMN_INFO_TYPE_FEATURE = "FEATURE"

_logger = logging.getLogger(__name__)


@dataclass
class FeatureExecutionGroup:
    type: str  # could be FEATURE, ON_DEMAND, SOURCE
    features: Union[
        List[FeatureColumnInfo], List[OnDemandColumnInfo], List[SourceDataColumnInfo]
    ]


# Small number has high priority. Besides SOURCE, preferring FEATURE over ON_DEMAND in topological
# sorting to make sure ON_DEMAND columns after FEATURE in simple cases to align with previous
# assumption before implementing TLT.
# NOTE: changing this priority may cause performance regression, proceed with caution.
COLUMN_TYPE_PRIORITY = {
    COLUMN_INFO_TYPE_SOURCE: 0,
    COLUMN_INFO_TYPE_ON_DEMAND: 1,
    COLUMN_INFO_TYPE_FEATURE: 2,
}


class _GraphNode:
    def __init__(self, column_info: ColumnInfo):
        info = column_info.info
        self.column_info = column_info
        self.output_name = info.output_name

        if isinstance(column_info.info, SourceDataColumnInfo):
            self.input_names = set()
            self.type = COLUMN_INFO_TYPE_SOURCE
        elif isinstance(column_info.info, FeatureColumnInfo):
            self.input_names = set(info.lookup_key)
            self.type = COLUMN_INFO_TYPE_FEATURE
        elif isinstance(column_info.info, OnDemandColumnInfo):
            self.input_names = set(info.input_bindings.values())
            self.type = COLUMN_INFO_TYPE_ON_DEMAND
        else:
            raise ValueError("unknown column info type")

    def __str__(self):
        return "node<" + self.output_name + ">"

    def __repr__(self):
        return str(self)


def _column_info_sort_key(node: _GraphNode) -> Tuple[int, str]:
    """
    Returns a tuple of an int and a str as the sorting key for _GraphNode. Priority is determined by
    the first element and then use the second element to break ties.
    """
    return COLUMN_TYPE_PRIORITY[node.type], node.output_name


def _should_be_grouped(node: _GraphNode) -> bool:
    """
    Returns True if the given node is of type that should be grouped together as much as possible.
    """
    return node.type == COLUMN_INFO_TYPE_FEATURE


def _validate_graph_depth(nodes: List[_GraphNode], depth_limit: int):
    name_to_node = {node.output_name: node for node in nodes}
    visited_depth = {}

    def dfs(node: _GraphNode, depth: int):
        if depth > depth_limit:
            raise ValueError(
                f"The given graph contains a dependency path longer than the limit {depth_limit}"
            )
        if (
            node.output_name in visited_depth
            and depth <= visited_depth[node.output_name]
        ):
            return
        visited_depth[node.output_name] = depth
        for column_name in node.input_names:
            dependency = name_to_node[column_name]
            dfs(dependency, depth + 1)

    for node in nodes:
        dfs(node, 1)


def get_encoded_graph_map(column_infos: List[ColumnInfo]) -> Dict[str, List[str]]:
    """
    Creates a dictionary of columns with their dependency columns for metric use. Columns are
    encoded with a string representing the type and index. For example:
      {
        "f3": ["s1", "s2"],
        "o4": ["f3"],
        "o5": []
      }
    "s1" and "s2" are SourceColumnInfos, "f3" is FeatureColumnInfo and "o4", "o5" are
    OnDemandColumnInfos. "f3" depends on "s1" and "s2", "o5" doesn't depend on any column, etc.
    :param column_infos: A list of ColumnInfos.
    """
    nodes = {info.output_name: _GraphNode(info) for info in column_infos}
    next_node_index = 0
    # A map from column info's output_name to its label.
    node_label = {}

    def get_node_label(node):
        nonlocal next_node_index
        output_name = node.output_name
        if output_name not in node_label:
            if node.type == COLUMN_INFO_TYPE_SOURCE:
                type_simple_str = "s"
            if node.type == COLUMN_INFO_TYPE_FEATURE:
                type_simple_str = "f"
            if node.type == COLUMN_INFO_TYPE_ON_DEMAND:
                type_simple_str = "o"
            new_label = type_simple_str + str(next_node_index)
            next_node_index += 1
            node_label[output_name] = new_label
        return node_label[output_name]

    graph_map = {}
    for node in nodes.values():
        label = get_node_label(node)
        dependencies = []
        for dep_name in sorted(node.input_names):
            if dep_name not in nodes:
                # skip the column if it's not in the feature spec.
                continue
            dep = get_node_label(nodes[dep_name])
            dependencies.append(dep)
        graph_map[label] = dependencies
    return graph_map


def assign_topological_ordering(
    column_infos: List[ColumnInfo],
    allow_missing_source_columns=False,
    graph_depth_limit=DEFAULT_GRAPH_DEPTH_LIMIT,
) -> List[ColumnInfo]:
    """
    Assigns the topological ordering for each ColumnInfo of the input. Returns a list of new
    ColumnInfo objects with topological_ordering set to an integer.

    :param column_infos: a list of ColumnInfos.
    :param allow_missing_source_columns: ONLY USED BY FSE TEMPORARILY. Allow lookup key or
    function input be missing from source columns. If true, this method will assign
    topological_ordering to columns as if the missing sources are added in the column_infos.
    :param graph_depth_limit raises if the given graph exceed the limit.
    :raises ValueError if there is a cycle in the graph.
    """
    nodes = list(map(lambda c: _GraphNode(c), column_infos))
    # allow_missing_source_columns is used when feature_serving_endpoint_client creates training
    # sets. It doesn't include source columns in the dataframe.
    # TODO[ML-33809]: clean up allow_missing_source_columns.
    all_output_names = set([n.output_name for n in nodes])
    all_input_names = reduce(lambda a, b: a | b, [n.input_names for n in nodes])
    missing_inputs = all_input_names - all_output_names
    if allow_missing_source_columns:
        for input_name in missing_inputs:
            if input_name not in all_output_names:
                nodes.append(
                    _GraphNode(ColumnInfo(SourceDataColumnInfo(input_name), False))
                )
    elif len(missing_inputs) > 0:
        missing_input_names_str = ", ".join(
            [f"'{name}'" for name in sorted(missing_inputs)]
        )
        raise ValueError(
            f"Input columns {missing_input_names_str} required by FeatureLookups or "
            "FeatureFunctions are not provided by input DataFrame or other FeatureFunctions and "
            "FeatureLookups"
        )
    output_name_to_node = {node.output_name: node for node in nodes}
    graph = {
        node: [output_name_to_node[input_name] for input_name in node.input_names]
        for node in nodes
    }
    sorted_nodes = topological_sort(graph, _column_info_sort_key, _should_be_grouped)
    # validate depth after sorting the graph because cycle is detected during sorting.
    _validate_graph_depth(nodes, graph_depth_limit)
    name_to_ordering = {node.output_name: i for i, node in enumerate(sorted_nodes)}
    return [
        column.with_topological_ordering(name_to_ordering[column.output_name])
        for column in column_infos
    ]


def get_feature_execution_groups(
    feature_spec: FeatureSpec, df_columns: List[str] = []
) -> List[FeatureExecutionGroup]:
    """
    Splits the list of column_infos in feature_spec into groups based on the topological_ordering of
    the column_infos such that each group contains only one type of feature columns and columns
    don't depend on other columns in the same group. The type of feature column is equivalent to the
    class type of column_info.info field.
    Example:
        Given FeatureSpec with some columns, after sorting the columns by topological_ordering,
        assuming the sorted list:
            [source_1, feature_2, feature_3, on_demand_4, on_demand_5]
        where feature_2 depends on feature_3. The resulting groups will be:
            [
                group(SOURCE, [source_1]),
                group(FEATURE, [feature_2]),
                group(FEATURE, [feature_3]),
                group(ON_DEMAND, [on_demand_4, on_demand_5]),
            ]

    :param feature_spec: A FeatureSpec with topologically sorted column_infos.
    :param df_columns: the columns from the DF used to create_training_set or score_batch.
    """
    # convert column infos into _GraphNode
    nodes = list(map(lambda c: _GraphNode(c), feature_spec.column_infos))
    if any(info.topological_ordering is None for info in feature_spec.column_infos):
        # The old version of feature_spec may not have topological_ordering, we can safely assume
        # they are already sorted because of validations during the feature_spec creation.
        _logger.warning(
            "Processing a feature spec that at least one of the column_infos has no "
            "topological_ordering"
        )
    else:
        # sort nodes by topological_ordering
        nodes = sorted(nodes, key=lambda n: n.column_info.topological_ordering)
    # A buffer holding the columns in a group.
    buffer = []
    # output names of columns in the current buffer.
    buffered_output_names = set()
    # Used to validate the topological sorting.
    # df_columns is used to be backward compatible. In old FeatureSpecs, source columns might not
    # exist. So we need to consider the df as initial resolved columns.
    resolved_columns = set(df_columns)
    result_list = []
    last_type = None
    for node in nodes:
        if not node.input_names.issubset(resolved_columns):
            raise ValueError(
                "The column_infos in the FeatureSpec is not topologically sorted"
            )
        if node.type != last_type or buffered_output_names.intersection(
            node.input_names
        ):
            # split group if the current node has a different type from the previous node OR
            # any of the inputs are from the nodes in the current group.
            if buffer:
                result_list.append(FeatureExecutionGroup(last_type, buffer))
                buffer = []
            buffered_output_names.clear()
            last_type = node.type
        buffer.append(node.column_info.info)
        resolved_columns.add(node.output_name)
        buffered_output_names.add(node.output_name)
    if buffer:
        result_list.append(FeatureExecutionGroup(last_type, buffer))
    return result_list


def convert_to_yaml_string(feature_spec: FeatureSpec) -> str:
    """
    Converts the given FeatureSpec to a YAML string.
    """
    feature_spec_dict = feature_spec._to_dict()
    return yaml.dump(
        feature_spec_dict,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        Dumper=YamlSafeDumper,
    )
