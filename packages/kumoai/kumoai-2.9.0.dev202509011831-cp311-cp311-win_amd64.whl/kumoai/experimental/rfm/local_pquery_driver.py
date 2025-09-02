import warnings
from typing import Dict, List, Literal, Optional, Tuple, Union

import numpy as np
import pandas as pd
from kumoapi.pquery import QueryType
from kumoapi.rfm import PQueryDefinition

import kumoai.kumolib as kumolib
from kumoai.experimental.rfm.local_graph_store import LocalGraphStore
from kumoai.experimental.rfm.pquery import PQueryPandasBackend

_coverage_warned = False


class LocalPQueryDriver:
    def __init__(
        self,
        graph_store: LocalGraphStore,
        query: PQueryDefinition,
        random_seed: Optional[int],
    ) -> None:
        self._graph_store = graph_store
        self._query = query
        self._random_seed = random_seed
        self._rng = np.random.default_rng(random_seed)

    def _get_candidates(
        self,
        anchor_time: Union[pd.Timestamp, Literal['entity']],
        exclude_node: Optional[np.ndarray] = None,
    ) -> np.ndarray:

        if self._query.query_type == QueryType.TEMPORAL:
            assert exclude_node is None

        table_name = self._query.entity.pkey.table_name
        num_nodes = len(self._graph_store.df_dict[table_name])
        mask_dict = self._graph_store.mask_dict

        candidate: np.ndarray

        # Case 1: All nodes are valid and nothing to exclude:
        if exclude_node is None and table_name not in mask_dict:
            candidate = np.arange(num_nodes)

        # Case 2: Not all nodes are valid - lookup valid nodes:
        if exclude_node is None:
            pkey_map = self._graph_store.pkey_map_dict[table_name]
            candidate = pkey_map['arange'].to_numpy().copy()

        # Case 3: Exclude nodes - use a mask to exclude them:
        else:
            mask = np.full((num_nodes, ), fill_value=True, dtype=bool)
            mask[exclude_node] = False
            if table_name in mask_dict:
                mask &= mask_dict[table_name]
            candidate = mask.nonzero()[0]

        self._rng.shuffle(candidate)

        return candidate

    def collect_test(
        self,
        size: int,
        anchor_time: Union[pd.Timestamp, Literal['entity']],
        batch_size: Optional[int] = None,
        max_iterations: int = 20,
    ) -> Tuple[np.ndarray, pd.Series, pd.Series]:
        r"""Collects test nodes and their labels used for evaluation.

        Args:
            size: The number of test nodes to collect.
            anchor_time: The anchor time.
            batch_size: How many nodes to process in a single batch.
            max_iterations: The number of steps to run before aborting.

        Returns:
            A triplet holding the nodes, timestamps and labels.
        """
        batch_size = size if batch_size is None else batch_size

        candidate = self._get_candidates(anchor_time)

        nodes: List[np.ndarray] = []
        times: List[pd.Series] = []
        ys: List[pd.Series] = []

        reached_end = False
        num_labels = candidate_offset = 0
        for _ in range(max_iterations):
            node = candidate[candidate_offset:candidate_offset + batch_size]

            if isinstance(anchor_time, pd.Timestamp):
                # Filter out non-existent entities:
                time = self._graph_store.time_dict.get(
                    self._query.entity.pkey.table_name)
                if time is not None:
                    node = node[time[node] <= (anchor_time.value // (1000**3))]

            if isinstance(anchor_time, pd.Timestamp):
                time = pd.Series(anchor_time).repeat(len(node))
                time = time.astype('datetime64[ns]').reset_index(drop=True)
            else:
                assert anchor_time == 'entity'
                time = self._graph_store.time_dict[
                    self._query.entity.pkey.table_name]
                time = pd.Series(time[node] * 1000**3, dtype='datetime64[ns]')

            y, mask = self(node, time)

            nodes.append(node[mask])
            times.append(time[mask].reset_index(drop=True))
            ys.append(y)

            num_labels += len(y)

            if num_labels > size:
                reached_end = True
                break  # Sufficient number of labels collected. Abort.

            candidate_offset += batch_size
            if candidate_offset >= len(candidate):
                reached_end = True
                break

        if len(nodes) > 1:
            node = np.concatenate(nodes, axis=0)[:size]
            time = pd.concat(times, axis=0).reset_index(drop=True).iloc[:size]
            y = pd.concat(ys, axis=0).reset_index(drop=True).iloc[:size]
        else:
            node = nodes[0][:size]
            time = times[0].iloc[:size]
            y = ys[0].iloc[:size]

        if len(node) == 0:
            raise RuntimeError("Failed to collect any test examples for "
                               "evaluation. Is your predictive query too "
                               "restrictive?")

        global _coverage_warned
        if not _coverage_warned and not reached_end and len(node) < size // 2:
            _coverage_warned = True
            warnings.warn(f"Failed to collect {size:,} test examples within "
                          f"{max_iterations} iterations. To improve coverage, "
                          f"consider increasing the number of PQ iterations "
                          f"using the 'max_pq_iterations' option. This "
                          f"warning will not be shown again in this run.")

        return node, time, y

    def collect_train(
        self,
        size: int,
        anchor_time: Union[pd.Timestamp, Literal['entity']],
        exclude_node: Optional[np.ndarray] = None,
        batch_size: Optional[int] = None,
        max_iterations: int = 20,
    ) -> Tuple[np.ndarray, pd.Series, pd.Series]:
        r"""Collects training nodes and their labels.

        Args:
            size: The number of test nodes to collect.
            anchor_time: The anchor time.
            exclude_node: The nodes to exclude for use as in-context examples.
            batch_size: How many nodes to process in a single batch.
            max_iterations: The number of steps to run before aborting.

        Returns:
            A triplet holding the nodes, timestamps and labels.
        """
        batch_size = size if batch_size is None else batch_size

        candidate = self._get_candidates(anchor_time, exclude_node)

        if len(candidate) == 0:
            raise RuntimeError("Failed to generate any context examples "
                               "since not enough entities exist")

        nodes: List[np.ndarray] = []
        times: List[pd.Series] = []
        ys: List[pd.Series] = []

        if isinstance(anchor_time, pd.Timestamp):
            anchor_time = anchor_time - self._query.target.end_offset

        reached_end = False
        num_labels = candidate_offset = 0
        for _ in range(max_iterations):
            node = candidate[candidate_offset:candidate_offset + batch_size]

            if isinstance(anchor_time, pd.Timestamp):
                # Filter out non-existent entities:
                time = self._graph_store.time_dict.get(
                    self._query.entity.pkey.table_name)
                if time is not None:
                    node = node[time[node] <= (anchor_time.value // (1000**3))]

            if isinstance(anchor_time, pd.Timestamp):
                time = pd.Series(anchor_time).repeat(len(node))
                time = time.astype('datetime64[ns]').reset_index(drop=True)
            else:
                assert anchor_time == 'entity'
                time = self._graph_store.time_dict[
                    self._query.entity.pkey.table_name]
                time = pd.Series(time[node] * 1000**3, dtype='datetime64[ns]')

            y, mask = self(node, time)

            nodes.append(node[mask])
            times.append(time[mask].reset_index(drop=True))
            ys.append(y)

            num_labels += len(y)

            if num_labels > size:
                reached_end = True
                break  # Sufficient number of labels collected. Abort.

            candidate_offset += batch_size
            if candidate_offset >= len(candidate):
                # Restart with an earlier anchor time (if applicable).
                if self._query.query_type == QueryType.STATIC:
                    reached_end = True
                    break  # Cannot jump back in time for static PQs. Abort.
                if anchor_time == 'entity':
                    reached_end = True
                    break
                candidate_offset = 0
                anchor_time = anchor_time - self._query.target.end_offset
                if anchor_time < self._graph_store.min_time:
                    reached_end = True
                    break  # No earlier anchor time left. Abort.

        if len(nodes) > 1:
            node = np.concatenate(nodes, axis=0)[:size]
            time = pd.concat(times, axis=0).reset_index(drop=True).iloc[:size]
            y = pd.concat(ys, axis=0).reset_index(drop=True).iloc[:size]
        else:
            node = nodes[0][:size]
            time = times[0].iloc[:size]
            y = ys[0].iloc[:size]

        if len(node) == 0:
            raise ValueError("Failed to collect any context examples. Is your "
                             "predictive query too restrictive?")

        global _coverage_warned
        if not _coverage_warned and not reached_end and len(node) < size // 2:
            _coverage_warned = True
            warnings.warn(f"Failed to collect {size:,} context examples "
                          f"within {max_iterations} iterations. To improve "
                          f"coverage, consider increasing the number of PQ "
                          f"iterations using the 'max_pq_iterations' option. "
                          f"This warning will not be shown again in this run.")

        return node, time, y

    def __call__(
        self,
        node: np.ndarray,
        anchor_time: pd.Series,
    ) -> Tuple[pd.Series, np.ndarray]:

        specs = self._query.get_sampling_specs(self._graph_store.edge_types)
        num_hops = max([spec.hop for spec in specs] + [0])
        num_neighbors: Dict[Tuple[str, str, str], list[int]] = {}
        time_offsets: Dict[
            Tuple[str, str, str],
            List[List[Optional[int]]],
        ] = {}
        for spec in specs:
            if spec.end_offset is not None:
                if spec.edge_type not in time_offsets:
                    time_offsets[spec.edge_type] = [[0, 0]
                                                    for _ in range(num_hops)]
                offset: Optional[int] = _date_offset_to_seconds(
                    spec.end_offset)
                time_offsets[spec.edge_type][spec.hop - 1][1] = offset
                if spec.start_offset is not None:
                    offset = _date_offset_to_seconds(spec.start_offset)
                else:
                    offset = None
                time_offsets[spec.edge_type][spec.hop - 1][0] = offset
            else:
                if spec.edge_type not in num_neighbors:
                    num_neighbors[spec.edge_type] = [0] * num_hops
                num_neighbors[spec.edge_type][spec.hop - 1] = -1

        edge_types = list(num_neighbors.keys()) + list(time_offsets.keys())
        node_types = list(
            set([self._query.entity.pkey.table_name])
            | set(src for src, _, _ in edge_types)
            | set(dst for _, _, dst in edge_types))

        sampler = kumolib.NeighborSampler(
            node_types,
            edge_types,
            {
                '__'.join(edge_type): self._graph_store.colptr_dict[edge_type]
                for edge_type in edge_types
            },
            {
                '__'.join(edge_type): self._graph_store.row_dict[edge_type]
                for edge_type in edge_types
            },
            {
                node_type: time
                for node_type, time in self._graph_store.time_dict.items()
                if node_type in node_types
            },
        )

        anchor_time = anchor_time.astype('datetime64[ns]')
        _, _, node_dict, batch_dict, _, _ = sampler.sample(
            {
                '__'.join(edge_type): np.array(values)
                for edge_type, values in num_neighbors.items()
            },
            {
                '__'.join(edge_type): np.array(values)
                for edge_type, values in time_offsets.items()
            },
            self._query.entity.pkey.table_name,
            node,
            anchor_time.astype(int).to_numpy() // 1000**3,
        )

        feat_dict: Dict[str, pd.DataFrame] = {}
        time_dict: Dict[str, pd.Series] = {}
        column_dict = self._query.column_dict
        time_tables = self._query.time_tables
        for table_name in set(list(column_dict.keys()) + time_tables):
            df = self._graph_store.df_dict[table_name]
            row_id = node_dict[table_name]
            df = df.iloc[row_id].reset_index(drop=True)
            if table_name in column_dict:
                feat_dict[table_name] = df[list(column_dict[table_name])]
            if table_name in time_tables:
                time_col = self._graph_store.time_column_dict[table_name]
                time_dict[table_name] = df[time_col]

        y, mask = PQueryPandasBackend().eval_pquery(
            query=self._query,
            feat_dict=feat_dict,
            time_dict=time_dict,
            batch_dict=batch_dict,
            anchor_time=anchor_time,
        )

        return y, mask


def _date_offset_to_seconds(offset: pd.DateOffset) -> int:
    r"""Convert a :class:`pandas.DateOffset` into a maximum number of
    nanoseconds.

    .. note::
        We are conservative and take months and years as their maximum value.
        Additional values are then dropped in label computation where we know
        the actual dates.
    """
    # Max durations for months and years in nanoseconds:
    MAX_DAYS_IN_MONTH = 31
    MAX_DAYS_IN_YEAR = 366

    # Conversion factors:
    SECONDS_IN_MINUTE = 60
    SECONDS_IN_HOUR = 60 * SECONDS_IN_MINUTE
    SECONDS_IN_DAY = 24 * SECONDS_IN_HOUR

    total_ns = 0
    multiplier = getattr(offset, 'n', 1)  # The multiplier (if present).

    for attr, value in offset.__dict__.items():
        if value is None or value == 0:
            continue
        scaled_value = value * multiplier
        if attr == 'years':
            total_ns += scaled_value * MAX_DAYS_IN_YEAR * SECONDS_IN_DAY
        elif attr == 'months':
            total_ns += scaled_value * MAX_DAYS_IN_MONTH * SECONDS_IN_DAY
        elif attr == 'days':
            total_ns += scaled_value * SECONDS_IN_DAY
        elif attr == 'hours':
            total_ns += scaled_value * SECONDS_IN_HOUR
        elif attr == 'minutes':
            total_ns += scaled_value * SECONDS_IN_MINUTE
        elif attr == 'seconds':
            total_ns += scaled_value

    return total_ns
