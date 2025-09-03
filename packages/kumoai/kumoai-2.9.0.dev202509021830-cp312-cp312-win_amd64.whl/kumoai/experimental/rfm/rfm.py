import json
import warnings
from typing import List, Literal, Optional, Union

import numpy as np
import pandas as pd
from kumoapi.model_plan import RunMode
from kumoapi.pquery import QueryType
from kumoapi.rfm import (
    Context,
    PQueryDefinition,
    RFMEvaluateRequest,
    RFMPredictRequest,
    RFMValidateQueryRequest,
)
from kumoapi.task import TaskType

from kumoai import global_state
from kumoai.exceptions import HTTPException
from kumoai.experimental.rfm import LocalGraph
from kumoai.experimental.rfm.local_graph_sampler import LocalGraphSampler
from kumoai.experimental.rfm.local_graph_store import LocalGraphStore
from kumoai.experimental.rfm.local_pquery_driver import LocalPQueryDriver
from kumoai.utils import InteractiveProgressLogger, ProgressLogger

_RANDOM_SEED = 42

_MAX_CONTEXT_SIZE = {
    RunMode.DEBUG: 100,
    RunMode.FAST: 1_000,
    RunMode.NORMAL: 5_000,
    RunMode.BEST: 10_000,
}
_MAX_TEST_SIZE = {  # Share test set size across run modes for fair comparison:
    RunMode.DEBUG: 100,
    RunMode.FAST: 2_000,
    RunMode.NORMAL: 2_000,
    RunMode.BEST: 2_000,
}

_MAX_SIZE = 30 * 1024 * 1024
_SIZE_LIMIT_MSG = ("Context size exceeds the 30MB limit. {stats_msg}\nPlease "
                   "reduce either the number of tables in the graph, their "
                   "number of columns (e.g., large text columns), "
                   "neighborhood configuration, or the run mode. If none of "
                   "this is possible, please create a feature request at "
                   "'https://github.com/kumo-ai/kumo-rfm' if you must go "
                   "beyond this for your use-case.")


class KumoRFM:
    r"""The Kumo Relational Foundation model (RFM) from the `KumoRFM: A
    Foundation Model for In-Context Learning on Relational Data
    <https://kumo.ai/research/kumo_relational_foundation_model.pdf>`_ paper.

    :class:`KumoRFM` is a foundation model to generate predictions for any
    relational dataset without training.
    The model is pre-trained and the class provides an interface to query the
    model from a :class:`LocalGraph` object.

    .. code-block:: python

        from kumoai.experimental.rfm import LocalGraph, KumoRFM

        df_users = pd.DataFrame(...)
        df_items = pd.DataFrame(...)
        df_orders = pd.DataFrame(...)

        graph = LocalGraph.from_data({
            'users': df_users,
            'items': df_items,
            'orders': df_orders,
        })

        rfm = KumoRFM(graph)

        query = ("PREDICT COUNT(transactions.*, 0, 30, days)>0 "
                 "FOR users.user_id=0")
        result = rfm.query(query)

        print(result)  # user_id  COUNT(transactions.*, 0, 30, days) > 0
                       # 1        0.85

    Args:
        graph: The graph.
        preprocess: Whether to pre-process the data in advance during graph
            materialization.
            This is a runtime trade-off between graph materialization and model
            processing speed.
            It can be benefical to preprocess your data once and then run many
            queries on top to achieve maximum model speed.
            However, if activiated, graph materialization can take potentially
            much longer, especially on graphs with many large text columns.
            Best to tune this option manually.
        verbose: Whether to print verbose output.
    """
    def __init__(
        self,
        graph: LocalGraph,
        preprocess: bool = False,
        verbose: Union[bool, ProgressLogger] = True,
    ) -> None:
        graph = graph.validate()
        self._graph_def = graph._to_api_graph_definition()
        self._graph_store = LocalGraphStore(graph, preprocess, verbose)
        self._graph_sampler = LocalGraphSampler(self._graph_store)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}()'

    def predict(
        self,
        query: str,
        *,
        anchor_time: Union[pd.Timestamp, Literal['entity'], None] = None,
        run_mode: Union[RunMode, str] = RunMode.FAST,
        num_neighbors: Optional[List[int]] = None,
        num_hops: int = 2,
        max_pq_iterations: int = 20,
        random_seed: Optional[int] = _RANDOM_SEED,
        verbose: Union[bool, ProgressLogger] = True,
    ) -> pd.DataFrame:
        """Returns predictions for a predictive query.

        Args:
            query: The predictive query.
            anchor_time: The anchor timestamp for the query. If set to
                :obj:`None`, will use the maximum timestamp in the data.
                If set to :`"entity"`, will use the timestamp of the entity.
            run_mode: The :class:`RunMode` for the query.
            num_neighbors: The number of neighbors to sample for each hop.
                If specified, the ``num_hops`` option will be ignored.
            num_hops: The number of hops to sample when generating the context.
            max_pq_iterations: The maximum number of iterations to perform to
                collect valid labels. It is advised to increase the number of
                iterations in case the predictive query has strict entity
                filters, in which case, :class:`KumoRFM` needs to sample more
                entities to find valid labels.
            random_seed: A manual seed for generating pseudo-random numbers.
            verbose: Whether to print verbose output.

        Returns:
            The predictions as a :class:`pandas.DataFrame`
        """
        explain = False
        query_def = self._parse_query(query)

        if num_hops != 2 and num_neighbors is not None:
            warnings.warn(f"Received custom 'num_neighbors' option; ignoring "
                          f"custom 'num_hops={num_hops}' option")

        if explain and run_mode in {RunMode.NORMAL, RunMode.BEST}:
            warnings.warn(f"Explainability is currently only supported for "
                          f"run mode 'FAST' (got '{run_mode}'). Provided run "
                          f"mode has been reset. Please lower the run mode to "
                          f"suppress this warning.")

        if explain:
            assert query_def.entity.ids is not None
            if len(query_def.entity.ids.value) > 1:
                raise ValueError(
                    f"Cannot explain predictions for more than a single "
                    f"entity (got {len(query_def.entity.ids.value)})")

        query_repr = query_def.to_string(rich=True, exclude_predict=True)
        if explain:
            msg = f'[bold]EXPLAIN[/bold] {query_repr}'
        else:
            msg = f'[bold]PREDICT[/bold] {query_repr}'

        if not isinstance(verbose, ProgressLogger):
            verbose = InteractiveProgressLogger(msg, verbose=verbose)

        with verbose as logger:
            context = self._get_context(
                query_def,
                anchor_time=anchor_time,
                run_mode=RunMode(run_mode),
                num_neighbors=num_neighbors,
                num_hops=num_hops,
                max_pq_iterations=max_pq_iterations,
                evaluate=False,
                random_seed=random_seed,
                logger=logger,
            )
            request = RFMPredictRequest(
                context=context,
                run_mode=RunMode(run_mode),
            )
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', message='Protobuf gencode')
                request_msg = request.to_protobuf()
                request_bytes = request_msg.SerializeToString()
            logger.log(f"Generated context of size "
                       f"{len(request_bytes) / (1024*1024):.2f}MB")

            if len(request_bytes) > _MAX_SIZE:
                stats_msg = Context.get_memory_stats(request_msg.context)
                raise ValueError(_SIZE_LIMIT_MSG.format(stats_msg=stats_msg))

            try:
                if explain:
                    resp = global_state.client.rfm_api.explain(request_bytes)
                else:
                    resp = global_state.client.rfm_api.predict(request_bytes)
            except HTTPException as e:
                try:
                    msg = json.loads(e.detail)['detail']
                except Exception:
                    msg = e.detail
                raise RuntimeError(f"An unexpected exception occurred. "
                                   f"Please create an issue at "
                                   f"'https://github.com/kumo-ai/kumo-rfm'. "
                                   f"{msg}") from None

        return pd.DataFrame(**resp.prediction)

    def evaluate(
        self,
        query: str,
        *,
        metrics: Optional[List[str]] = None,
        anchor_time: Union[pd.Timestamp, Literal['entity'], None] = None,
        run_mode: Union[RunMode, str] = RunMode.FAST,
        num_neighbors: Optional[List[int]] = None,
        num_hops: int = 2,
        max_pq_iterations: int = 20,
        random_seed: Optional[int] = _RANDOM_SEED,
        verbose: Union[bool, ProgressLogger] = True,
    ) -> pd.DataFrame:
        """Evaluates a predictive query.

        Args:
            query: The predictive query.
            metrics: The metrics to use.
            anchor_time: The anchor timestamp for the query. If set to
                :obj:`None`, will use the maximum timestamp in the data.
                If set to :`"entity"`, will use the timestamp of the entity.
            run_mode: The :class:`RunMode` for the query.
            num_neighbors: The number of neighbors to sample for each hop.
                If specified, the ``num_hops`` option will be ignored.
            num_hops: The number of hops to sample when generating the context.
            max_pq_iterations: The maximum number of iterations to perform to
                collect valid labels. It is advised to increase the number of
                iterations in case the predictive query has strict entity
                filters, in which case, :class:`KumoRFM` needs to sample more
                entities to find valid labels.
            random_seed: A manual seed for generating pseudo-random numbers.
            verbose: Whether to print verbose output.

        Returns:
            The metrics as a :class:`pandas.DataFrame`
        """
        query_def = self._parse_query(query)

        if num_hops != 2 and num_neighbors is not None:
            warnings.warn(f"Received custom 'num_neighbors' option; ignoring "
                          f"custom 'num_hops={num_hops}' option")

        query_repr = query_def.to_string(rich=True, exclude_predict=True)
        msg = f'[bold]EVALUATE[/bold] {query_repr}'

        if not isinstance(verbose, ProgressLogger):
            verbose = InteractiveProgressLogger(msg, verbose=verbose)

        with verbose as logger:
            context = self._get_context(
                query_def,
                anchor_time=anchor_time,
                run_mode=RunMode(run_mode),
                num_neighbors=num_neighbors,
                num_hops=num_hops,
                max_pq_iterations=max_pq_iterations,
                evaluate=True,
                random_seed=random_seed,
                logger=logger if verbose else None,
            )
            if metrics is not None and len(metrics) > 0:
                self._validate_metrics(metrics, context.task_type)
                metrics = list(dict.fromkeys(metrics))
            request = RFMEvaluateRequest(
                context=context,
                run_mode=RunMode(run_mode),
                metrics=metrics,
            )
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', message='Protobuf gencode')
                request_msg = request.to_protobuf()
                request_bytes = request_msg.SerializeToString()
            logger.log(f"Generated context of size "
                       f"{len(request_bytes) / (1024*1024):.2f}MB")

            if len(request_bytes) > _MAX_SIZE:
                stats_msg = Context.get_memory_stats(request_msg.context)
                raise ValueError(_SIZE_LIMIT_MSG.format(stats_msg=stats_msg))

            try:
                resp = global_state.client.rfm_api.evaluate(request_bytes)
            except HTTPException as e:
                try:
                    msg = json.loads(e.detail)['detail']
                except Exception:
                    msg = e.detail
                raise RuntimeError(f"An unexpected exception occurred. "
                                   f"Please create an issue at "
                                   f"'https://github.com/kumo-ai/kumo-rfm'. "
                                   f"{msg}") from None

        return pd.DataFrame.from_dict(
            resp.metrics,
            orient='index',
            columns=['value'],
        ).reset_index(names='metric')

    def get_train_table(
        self,
        query: str,
        size: int,
        *,
        anchor_time: Union[pd.Timestamp, Literal['entity'], None] = None,
        random_seed: Optional[int] = _RANDOM_SEED,
        max_iterations: int = 20,
    ) -> pd.DataFrame:
        """Returns the labels of a predictive query for a specified anchor
        time.

        Args:
            query: The predictive query.
            size: The maximum number of entities to generate labels for.
            anchor_time: The anchor timestamp for the query. If set to
                :obj:`None`, will use the maximum timestamp in the data.
                If set to :`"entity"`, will use the timestamp of the entity.
            random_seed: A manual seed for generating pseudo-random numbers.
            max_iterations: The number of steps to run before aborting.

        Returns:
            The labels as a :class:`pandas.DataFrame`.
        """
        query_def = self._parse_query(query)

        if anchor_time is None:
            anchor_time = self._graph_store.max_time
            anchor_time = anchor_time - query_def.target.end_offset

        assert anchor_time is not None
        if isinstance(anchor_time, pd.Timestamp):
            self._validate_time(query_def, anchor_time, evaluate=True)
        else:
            assert anchor_time == 'entity'
            if (query_def.entity.pkey.table_name
                    not in self._graph_store.time_dict):
                raise ValueError(f"Anchor time 'entity' requires the entity "
                                 f"table '{query_def.entity.pkey.table_name}' "
                                 f"to have a time column")

        query_driver = LocalPQueryDriver(self._graph_store, query_def,
                                         random_seed)

        node, time, y = query_driver.collect_test(
            size=size,
            anchor_time=anchor_time,
            batch_size=min(10_000, size),
            max_iterations=max_iterations,
        )

        return pd.DataFrame({
            'ENTITY': node,
            'ANCHOR_TIMESTAMP': time,
            'TARGET': y,
        })

    # Helpers #################################################################

    def _parse_query(self, query: str) -> PQueryDefinition:
        if isinstance(query, PQueryDefinition):
            return query

        if isinstance(query, str) and query.strip()[:9].lower() == 'evaluate ':
            raise ValueError("'EVALUATE PREDICT ...' queries are not "
                             "supported in the SDK. Instead, use either "
                             "`predict()` or `evaluate()` methods to perform "
                             "predictions or evaluations.")

        try:
            request = RFMValidateQueryRequest(
                query=query,
                graph_definition=self._graph_def,
            )

            resp = global_state.client.rfm_api.validate_query(request)
            # TODO Expose validation warnings.

            if len(resp.validation_response.warnings) > 0:
                msg = '\n'.join([
                    f'{i+1}. {warning.title}: {warning.message}' for i, warning
                    in enumerate(resp.validation_response.warnings)
                ])
                warnings.warn(f"Encountered the following warnings during "
                              f"parsing:\n{msg}")

            return resp.query_definition
        except HTTPException as e:
            try:
                msg = json.loads(e.detail)['detail']
            except Exception:
                msg = e.detail
            raise ValueError(f"Failed to parse query '{query}'. "
                             f"{msg}") from None

    def _validate_time(
        self,
        query: PQueryDefinition,
        anchor_time: pd.Timestamp,
        evaluate: bool,
    ) -> None:

        if self._graph_store.min_time == pd.Timestamp.max:
            return  # Graph without timestamps

        if anchor_time < self._graph_store.min_time:
            raise ValueError(f"Anchor timestamp '{anchor_time}' is before "
                             f"the earliest timestamp "
                             f"'{self._graph_store.min_time}' in the data.")

        if anchor_time - query.target.end_offset < self._graph_store.min_time:
            raise ValueError(f"Anchor timestamp is too early or aggregation "
                             f"time range is too large. To make this "
                             f"prediction, we would need data back to "
                             f"'{anchor_time - query.target.end_offset}', "
                             f"however, your data only contains data back to "
                             f"'{self._graph_store.min_time}'.")

        if (anchor_time - 2 * query.target.end_offset
                < self._graph_store.min_time):
            warnings.warn(f"Anchor timestamp is too early or aggregation "
                          f"time range is too large. To form proper input "
                          f"data, we would need data back to "
                          f"'{anchor_time - 2 * query.target.end_offset}', "
                          f"however, your data only contains data back to "
                          f"'{self._graph_store.min_time}'.")

        if (not evaluate and anchor_time
                > self._graph_store.max_time + pd.DateOffset(days=1)):
            warnings.warn(f"Anchor timestamp '{anchor_time}' is after the "
                          f"latest timestamp '{self._graph_store.max_time}' "
                          f"in the data. Please make sure this is intended.")

        if (evaluate and anchor_time
                > self._graph_store.max_time - query.target.end_offset):
            raise ValueError(
                f"Anchor timestamp for evaluation is after the latest "
                f"supported timestamp "
                f"'{self._graph_store.max_time - query.target.end_offset}'.")

    def _get_context(
        self,
        query: PQueryDefinition,
        anchor_time: Union[pd.Timestamp, Literal['entity'], None],
        run_mode: RunMode,
        num_neighbors: Optional[List[int]],
        num_hops: int,
        max_pq_iterations: int,
        evaluate: bool,
        random_seed: Optional[int] = _RANDOM_SEED,
        logger: Optional[ProgressLogger] = None,
    ) -> Context:

        if num_neighbors is not None:
            num_hops = len(num_neighbors)

        if num_hops < 0:
            raise ValueError(f"'num_hops' must be non-negative "
                             f"(got {num_hops})")
        if num_hops > 6:
            raise ValueError(f"Cannot predict on subgraphs with more than 6 "
                             f"hops (got {num_hops}). Please reduce the "
                             f"number of hops and try again. Please create a "
                             f"feature request at "
                             f"'https://github.com/kumo-ai/kumo-rfm' if you "
                             f"must go beyond this for your use-case.")

        query_driver = LocalPQueryDriver(self._graph_store, query, random_seed)
        task_type = query.get_task_type(
            stypes=self._graph_store.stype_dict,
            edge_types=self._graph_store.edge_types,
        )

        if logger is not None:
            if task_type == TaskType.BINARY_CLASSIFICATION:
                task_type_repr = 'binary classification'
            elif task_type == TaskType.MULTICLASS_CLASSIFICATION:
                task_type_repr = 'multi-class classification'
            elif task_type == TaskType.REGRESSION:
                task_type_repr = 'regression'
            elif task_type == TaskType.TEMPORAL_LINK_PREDICTION:
                task_type_repr = 'link prediction'
            else:
                task_type_repr = str(task_type)
            logger.log(f"Identified {query.query_type} {task_type_repr} task")

        if task_type.is_link_pred and num_hops < 2:
            raise ValueError(f"Cannot perform link prediction on subgraphs "
                             f"with less than 2 hops (got {num_hops}) since "
                             f"historical target entities need to be part of "
                             f"the context. Please increase the number of "
                             f"hops and try again.")

        if num_neighbors is None:
            if run_mode == RunMode.DEBUG:
                num_neighbors = [16, 16, 4, 4, 1, 1][:num_hops]
            elif run_mode == RunMode.FAST or task_type.is_link_pred:
                num_neighbors = [32, 32, 8, 8, 4, 4][:num_hops]
            else:
                num_neighbors = [64, 64, 8, 8, 4, 4][:num_hops]

        if anchor_time is None:
            anchor_time = self._graph_store.max_time
            if evaluate:
                anchor_time = anchor_time - query.target.end_offset
            if logger is not None:
                assert isinstance(anchor_time, pd.Timestamp)
                if (anchor_time.hour == 0 and anchor_time.minute == 0
                        and anchor_time.second == 0
                        and anchor_time.microsecond == 0):
                    logger.log(f"Derived anchor time {anchor_time.date()}")
                else:
                    logger.log(f"Derived anchor time {anchor_time}")

        assert anchor_time is not None
        if isinstance(anchor_time, pd.Timestamp):
            self._validate_time(query, anchor_time, evaluate)
        else:
            assert anchor_time == 'entity'
            if query.entity.pkey.table_name not in self._graph_store.time_dict:
                raise ValueError(f"Anchor time 'entity' requires the entity "
                                 f"table '{query.entity.pkey.table_name}' to "
                                 f"have a time column")

        y_test: Optional[pd.Series] = None
        if evaluate:
            max_test_size = _MAX_TEST_SIZE[run_mode]
            if task_type.is_link_pred:
                max_test_size = max_test_size // 5

            test_node, test_time, y_test = query_driver.collect_test(
                size=max_test_size,
                anchor_time=anchor_time,
                max_iterations=max_pq_iterations,
            )
            if logger is not None:
                if task_type == TaskType.BINARY_CLASSIFICATION:
                    pos = 100 * int((y_test > 0).sum()) / len(y_test)
                    msg = (f"Collected {len(y_test):,} test examples with "
                           f"{pos:.2f}% positive cases")
                elif task_type == TaskType.MULTICLASS_CLASSIFICATION:
                    msg = (f"Collected {len(y_test):,} test examples "
                           f"holding {y_test.nunique()} classes")
                elif task_type == TaskType.REGRESSION:
                    _min, _max = float(y_test.min()), float(y_test.max())
                    msg = (f"Collected {len(y_test):,} test examples with "
                           f"targets between {format_value(_min)} and "
                           f"{format_value(_max)}")
                elif task_type == TaskType.TEMPORAL_LINK_PREDICTION:
                    num_rhs = y_test.explode().nunique()
                    msg = (f"Collected {len(y_test):,} test examples with "
                           f"{num_rhs:,} unique items")
                else:
                    raise NotImplementedError
                logger.log(msg)

        else:
            assert query.entity.ids is not None

            max_num_test = 200 if task_type.is_link_pred else 1000
            if len(query.entity.ids.value) > max_num_test:
                raise ValueError(f"Cannot predict for more than "
                                 f"{max_num_test:,} entities at once "
                                 f"(got {len(query.entity.ids.value):,})")

            test_node = self._graph_store.get_node_id(
                table_name=query.entity.pkey.table_name,
                pkey=pd.Series(
                    query.entity.ids.value,
                    dtype=query.entity.ids.dtype,
                ),
            )

            if isinstance(anchor_time, pd.Timestamp):
                test_time = pd.Series(anchor_time).repeat(
                    len(test_node)).reset_index(drop=True)
            else:
                time = self._graph_store.time_dict[
                    query.entity.pkey.table_name]
                time = time[test_node] * 1000**3
                test_time = pd.Series(time, dtype='datetime64[ns]')

        train_node, train_time, y_train = query_driver.collect_train(
            size=_MAX_CONTEXT_SIZE[run_mode],
            anchor_time=anchor_time,
            exclude_node=test_node if (query.query_type == QueryType.STATIC
                                       or anchor_time == 'entity') else None,
            max_iterations=max_pq_iterations,
        )

        if logger is not None:
            if task_type == TaskType.BINARY_CLASSIFICATION:
                pos = 100 * int((y_train > 0).sum()) / len(y_train)
                msg = (f"Collected {len(y_train):,} in-context examples with "
                       f"{pos:.2f}% positive cases")
            elif task_type == TaskType.MULTICLASS_CLASSIFICATION:
                msg = (f"Collected {len(y_train):,} in-context examples "
                       f"holding {y_train.nunique()} classes")
            elif task_type == TaskType.REGRESSION:
                _min, _max = float(y_train.min()), float(y_train.max())
                msg = (f"Collected {len(y_train):,} in-context examples with "
                       f"targets between {format_value(_min)} and "
                       f"{format_value(_max)}")
            elif task_type == TaskType.TEMPORAL_LINK_PREDICTION:
                num_rhs = y_train.explode().nunique()
                msg = (f"Collected {len(y_train):,} in-context examples with "
                       f"{num_rhs:,} unique items")
            else:
                raise NotImplementedError
            logger.log(msg)

        entity_table_names = query.get_entity_table_names(
            self._graph_store.edge_types)

        # Exclude the entity anchor time from the feature set to prevent
        # running out-of-distribution between in-context and test examples:
        exclude_cols_dict = query.exclude_cols_dict
        if anchor_time == 'entity':
            if entity_table_names[0] not in exclude_cols_dict:
                exclude_cols_dict[entity_table_names[0]] = []
            time_column_dict = self._graph_store.time_column_dict
            time_column = time_column_dict[entity_table_names[0]]
            exclude_cols_dict[entity_table_names[0]].append(time_column)

        subgraph = self._graph_sampler(
            entity_table_names=entity_table_names,
            node=np.concatenate([train_node, test_node]),
            time=np.concatenate([
                train_time.astype('datetime64[ns]').astype(int).to_numpy(),
                test_time.astype('datetime64[ns]').astype(int).to_numpy(),
            ]),
            run_mode=run_mode,
            num_neighbors=num_neighbors,
            exclude_cols_dict=exclude_cols_dict,
        )

        return Context(
            task_type=task_type,
            entity_table_names=entity_table_names,
            subgraph=subgraph,
            y_train=y_train,
            y_test=y_test,
            top_k=query.top_k,
        )

    @staticmethod
    def _validate_metrics(
        metrics: List[str],
        task_type: TaskType,
    ) -> None:

        if task_type == TaskType.BINARY_CLASSIFICATION:
            supported_metrics = [
                'acc', 'precision', 'recall', 'f1', 'auroc', 'auprc', 'ap'
            ]
        elif task_type == TaskType.MULTICLASS_CLASSIFICATION:
            supported_metrics = ['acc', 'precision', 'recall', 'f1', 'mrr']
        elif task_type == TaskType.REGRESSION:
            supported_metrics = ['mae', 'mape', 'mse', 'rmse', 'smape']
        elif task_type == TaskType.TEMPORAL_LINK_PREDICTION:
            supported_metrics = [
                'map@', 'ndcg@', 'mrr@', 'precision@', 'recall@', 'f1@',
                'hit_ratio@'
            ]
        else:
            raise NotImplementedError

        for metric in metrics:
            if '@' in metric:
                metric_split = metric.split('@')
                if len(metric_split) != 2:
                    raise ValueError(f"Unsupported metric '{metric}'. "
                                     f"Available metrics "
                                     f"are {supported_metrics}.")

                name, top_k = f'{metric_split[0]}@', metric_split[1]

                if not top_k.isdigit():
                    raise ValueError(f"Metric '{metric}' does not define a "
                                     f"valid 'top_k' value (got '{top_k}').")

                if int(top_k) <= 0:
                    raise ValueError(f"Metric '{metric}' needs to define a "
                                     f"positive 'top_k' value (got '{top_k}')")

                if int(top_k) > 100:
                    raise ValueError(f"Metric '{metric}' defines a 'top_k' "
                                     f"value greater than 100 "
                                     f"(got '{top_k}'). Please create a "
                                     f"feature request at "
                                     f"'https://github.com/kumo-ai/kumo-rfm' "
                                     f"if you must go beyond this for your "
                                     f"use-case.")

                metric = name

            if metric not in supported_metrics:
                raise ValueError(f"Unsupported metric '{metric}'. Available "
                                 f"metrics are {supported_metrics}. If you "
                                 f"feel a metric is missing, please create a "
                                 f"feature request at "
                                 f"'https://github.com/kumo-ai/kumo-rfm'.")


def format_value(value: Union[int, float]) -> str:
    if value == int(value):
        return f'{int(value):,}'
    if abs(value) >= 1000:
        return f'{value:,.0f}'
    if abs(value) >= 10:
        return f'{value:.1f}'
    return f'{value:.2f}'
