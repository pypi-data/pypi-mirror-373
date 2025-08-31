from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from kumoapi.model_plan import RunMode
from kumoapi.rfm.context import EdgeLayout, Link, Subgraph, Table
from kumoapi.typing import Stype

import kumoai.kumolib as kumolib
from kumoai.experimental.rfm.local_graph_store import LocalGraphStore
from kumoai.experimental.rfm.utils import normalize_text


class LocalGraphSampler:
    def __init__(self, graph_store: LocalGraphStore) -> None:
        self._graph_store = graph_store
        self._sampler = kumolib.NeighborSampler(
            self._graph_store.node_types,
            self._graph_store.edge_types,
            {
                '__'.join(edge_type): colptr
                for edge_type, colptr in self._graph_store.colptr_dict.items()
            },
            {
                '__'.join(edge_type): row
                for edge_type, row in self._graph_store.row_dict.items()
            },
            self._graph_store.time_dict,
        )

    def __call__(
        self,
        entity_table_names: Tuple[str, ...],
        node: np.ndarray,
        time: np.ndarray,
        run_mode: RunMode,
        num_neighbors: List[int],
        exclude_cols_dict: Dict[str, List[str]],
    ) -> Subgraph:

        (
            row_dict,
            col_dict,
            node_dict,
            batch_dict,
            num_sampled_nodes_dict,
            num_sampled_edges_dict,
        ) = self._sampler.sample(
            {
                '__'.join(edge_type): num_neighbors
                for edge_type in self._graph_store.edge_types
            },
            {},  # time interval based sampling
            entity_table_names[0],
            node,
            time // 1000**3,  # nanoseconds to seconds
        )

        table_dict: Dict[str, Table] = {}
        for table_name, node in node_dict.items():
            batch = batch_dict[table_name]

            if len(node) == 0:
                continue

            df = self._graph_store.df_dict[table_name]

            num_sampled_nodes = num_sampled_nodes_dict[table_name].tolist()
            stype_dict = {  # Exclude target columns:
                column_name: stype
                for column_name, stype in
                self._graph_store.stype_dict[table_name].items()
                if column_name not in exclude_cols_dict.get(table_name, [])
            }
            primary_key: Optional[str] = None
            if table_name in entity_table_names:
                primary_key = self._graph_store.pkey_name_dict.get(table_name)

            columns: List[str] = []
            if table_name in entity_table_names:
                columns += [self._graph_store.pkey_name_dict[table_name]]
            columns += list(stype_dict.keys())

            if len(columns) == 0:
                table_dict[table_name] = Table(
                    df=pd.DataFrame(index=range(len(node))),
                    row=None,
                    batch=batch,
                    num_sampled_nodes=num_sampled_nodes,
                    stype_dict=stype_dict,
                    primary_key=primary_key,
                )
                continue

            # Only store unique rows in `df` above a certain threshold:
            unique_node, inverse_node = np.unique(node, return_inverse=True)
            if len(node) > 1.05 * len(unique_node):
                df = df.iloc[unique_node]
                row = inverse_node
            else:
                df = df.iloc[node]
                row = None
            df = df.reset_index(drop=True)

            # Filter data frame to minimal set of columns:
            df = df[columns]

            # Normalize text (if not already pre-processed):
            for column_name, stype in stype_dict.items():
                if stype == Stype.text:
                    df[column_name] = normalize_text(df[column_name])

            table_dict[table_name] = Table(
                df=df,
                row=row,
                batch=batch,
                num_sampled_nodes=num_sampled_nodes,
                stype_dict=stype_dict,
                primary_key=primary_key,
            )

        link_dict: Dict[Tuple[str, str, str], Link] = {}
        for edge_type in self._graph_store.edge_types:
            edge_type_str = '__'.join(edge_type)

            row = row_dict[edge_type_str]
            col = col_dict[edge_type_str]

            if len(row) == 0:
                continue

            # Do not store reverse edge type if it is a replica:
            rev_edge_type = Subgraph.rev_edge_type(edge_type)
            rev_edge_type_str = '__'.join(rev_edge_type)
            if (rev_edge_type in link_dict
                    and np.array_equal(row, col_dict[rev_edge_type_str])
                    and np.array_equal(col, row_dict[rev_edge_type_str])):
                link = Link(
                    layout=EdgeLayout.REV,
                    row=None,
                    col=None,
                    num_sampled_edges=(
                        num_sampled_edges_dict[edge_type_str].tolist()),
                )
                link_dict[edge_type] = link
                continue

            layout = EdgeLayout.COO
            if np.array_equal(row, np.arange(len(row))):
                row = None
            if np.array_equal(col, np.arange(len(col))):
                col = None

            # Store in compressed representation if more efficient:
            num_cols = table_dict[edge_type[2]].num_rows
            if col is not None and len(col) > num_cols + 1:
                layout = EdgeLayout.CSC
                colcount = np.bincount(col, minlength=num_cols)
                col = np.empty(num_cols + 1, dtype=col.dtype)
                col[0] = 0
                np.cumsum(colcount, out=col[1:])

            link = Link(
                layout=layout,
                row=row,
                col=col,
                num_sampled_edges=(
                    num_sampled_edges_dict[edge_type_str].tolist()),
            )
            link_dict[edge_type] = link

        return Subgraph(
            anchor_time=time,
            table_dict=table_dict,
            link_dict=link_dict,
        )
