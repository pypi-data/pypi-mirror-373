from typing import Dict, Optional, Tuple, Union

import numpy as np
import pandas as pd
from kumoapi.rfm import PQueryDefinition
from kumoapi.rfm.pquery import (
    Aggregation,
    AggregationType,
    BoolOp,
    Column,
    Condition,
    Filter,
    Float,
    FloatList,
    Int,
    IntList,
    LogicalOperation,
    MemberOp,
    RelOp,
    Str,
    StrList,
)

from kumoai.experimental.rfm.pquery import PQueryBackend


class PQueryPandasBackend(PQueryBackend[pd.DataFrame, pd.Series, np.ndarray]):
    def eval_aggregation_type(
        self,
        op: AggregationType,
        feat: Optional[pd.Series],
        batch: np.ndarray,
        batch_size: int,
        filter_na: bool = True,
    ) -> Tuple[pd.Series, np.ndarray]:

        if op != AggregationType.COUNT:
            assert feat is not None

        if feat is not None:
            mask = feat.notna()
            feat, batch = feat[mask], batch[mask]

        if op == AggregationType.LIST_DISTINCT:
            df = pd.DataFrame(dict(feat=feat, batch=batch))
            df = df.drop_duplicates()
            out = df.groupby('batch')['feat'].agg(list)

        else:
            df = pd.DataFrame(dict(feat=feat, batch=batch))
            if op == AggregationType.AVG:
                agg = 'mean'
            elif op == AggregationType.COUNT:
                agg = 'size'
            else:
                agg = op.lower()
            out = df.groupby('batch')['feat'].agg(agg)

            if not pd.api.types.is_datetime64_any_dtype(out):
                out = out.astype('float32')

        out.name = None
        out.index.name = None

        if op in {AggregationType.SUM, AggregationType.COUNT}:
            out = out.reindex(range(batch_size), fill_value=0)
            mask = np.ones(batch_size, dtype=bool)
            return out, mask

        mask = np.zeros(batch_size, dtype=bool)
        mask[batch] = True

        if filter_na:
            return out.reset_index(drop=True), mask

        out = out.reindex(range(batch_size), fill_value=pd.NA)

        return out, mask

    def eval_rel_op(
        self,
        left: pd.Series,
        op: RelOp,
        right: Union[Int, Float, Str, None],
    ) -> pd.Series:

        if right is None:
            if op == RelOp.EQ:
                return left.isna()
            assert op == RelOp.NEQ
            return left.notna()

        value = pd.Series([right.value], dtype=left.dtype).iloc[0]

        if op == RelOp.EQ:
            return (left == value).fillna(False).astype(bool)
        if op == RelOp.NEQ:
            out = (left != value).fillna(False).astype(bool)
            out[left.isna()] = False  # N/A != right should always be `False`.
            return out
        if op == RelOp.LEQ:
            return (left <= value).fillna(False).astype(bool)
        if op == RelOp.GEQ:
            return (left >= value).fillna(False).astype(bool)
        if op == RelOp.LT:
            return (left < value).fillna(False).astype(bool)
        if op == RelOp.GT:
            return (left > value).fillna(False).astype(bool)

        raise NotImplementedError(f"Operator '{op}' not implemented")

    def eval_member_op(
        self,
        left: pd.Series,
        op: MemberOp,
        right: Union[IntList, FloatList, StrList],
    ) -> pd.Series:

        if op == MemberOp.IN:
            ser = pd.Series(right.value, dtype=left.dtype)
            return left.isin(ser).astype(bool)

        raise NotImplementedError(f"Operator '{op}' not implemented")

    def eval_bool_op(
        self,
        left: pd.Series,
        op: BoolOp,
        right: Optional[pd.Series],
    ) -> pd.Series:

        # TODO Implement Kleene-Priest three-value logic.
        if op == BoolOp.AND:
            assert right is not None
            return left & right
        if op == BoolOp.OR:
            assert right is not None
            return left | right
        if op == BoolOp.NOT:
            return ~left

        raise NotImplementedError(f"Operator '{op}' not implemented")

    def eval_column(
        self,
        column: Column,
        feat_dict: Dict[str, pd.DataFrame],
        filter_na: bool = True,
    ) -> Tuple[pd.Series, np.ndarray]:

        out = feat_dict[column.table_name][column.column_name]
        out = out.reset_index(drop=True)

        if pd.api.types.is_float_dtype(out):
            out = out.astype('float32')

        out.name = None
        out.index.name = None

        mask = out.notna().to_numpy()

        if not filter_na:
            return out, mask

        out = out[mask].reset_index(drop=True)

        # Cast to primitive dtype:
        if pd.api.types.is_integer_dtype(out):
            out = out.astype('int64')
        elif pd.api.types.is_bool_dtype(out):
            out = out.astype('bool')

        return out, mask

    def eval_aggregation(
        self,
        aggr: Aggregation,
        feat_dict: Dict[str, pd.DataFrame],
        time_dict: Dict[str, pd.Series],
        batch_dict: Dict[str, np.ndarray],
        anchor_time: pd.Series,
        filter_na: bool = True,
    ) -> Tuple[pd.Series, np.ndarray]:

        target_table = aggr.column.table_name
        target_batch = batch_dict[target_table]
        target_time = time_dict[target_table]
        anchor_target_time = anchor_time[target_batch].reset_index(drop=True)

        target_mask = target_time <= anchor_target_time + aggr.end_offset

        if aggr.start is not None:
            start_offset = aggr.start * aggr.time_unit.to_offset()
            target_mask &= target_time > anchor_target_time + start_offset

        if aggr.filter is not None:
            target_mask &= self.eval_filter(
                filter=aggr.filter,
                feat_dict=feat_dict,
                time_dict=time_dict,
                batch_dict=batch_dict,
                anchor_time=anchor_time,
            )

        if (aggr.type == AggregationType.COUNT
                and aggr.column.column_name == '*'):
            target_feat = None
        else:
            target_feat, _ = self.eval_column(
                aggr.column,
                feat_dict,
                filter_na=False,
            )
            target_feat = target_feat[target_mask]

        return self.eval_aggregation_type(
            aggr.type,
            feat=target_feat,
            batch=target_batch[target_mask],
            batch_size=len(anchor_time),
            filter_na=filter_na,
        )

    def eval_condition(
        self,
        condition: Condition,
        feat_dict: Dict[str, pd.DataFrame],
        time_dict: Dict[str, pd.Series],
        batch_dict: Dict[str, np.ndarray],
        anchor_time: pd.Series,
        filter_na: bool = True,
    ) -> Tuple[pd.Series, np.ndarray]:

        if isinstance(condition.left, Column):
            left, mask = self.eval_column(
                column=condition.left,
                feat_dict=feat_dict,
                filter_na=filter_na if condition.right is not None else False,
            )
        else:
            assert isinstance(condition.left, Aggregation)
            left, mask = self.eval_aggregation(
                aggr=condition.left,
                feat_dict=feat_dict,
                time_dict=time_dict,
                batch_dict=batch_dict,
                anchor_time=anchor_time,
                filter_na=filter_na if condition.right is not None else False,
            )

        if filter_na and condition.right is None:
            mask = np.ones(len(left), dtype=bool)

        if isinstance(condition.op, RelOp):
            out = self.eval_rel_op(
                left=left,
                op=condition.op,
                right=condition.right,
            )
        else:
            assert isinstance(condition.op, MemberOp)
            out = self.eval_member_op(
                left=left,
                op=condition.op,
                right=condition.right,
            )

        return out, mask

    def eval_logical_operation(
        self,
        logical_operation: LogicalOperation,
        feat_dict: Dict[str, pd.DataFrame],
        time_dict: Dict[str, pd.Series],
        batch_dict: Dict[str, np.ndarray],
        anchor_time: pd.Series,
        filter_na: bool = True,
    ) -> Tuple[pd.Series, np.ndarray]:

        if isinstance(logical_operation.left, Condition):
            left, mask = self.eval_condition(
                condition=logical_operation.left,
                feat_dict=feat_dict,
                time_dict=time_dict,
                batch_dict=batch_dict,
                anchor_time=anchor_time,
                filter_na=False,
            )
        else:
            assert isinstance(logical_operation.left, LogicalOperation)
            left, mask = self.eval_logical_operation(
                logical_operation=logical_operation.left,
                feat_dict=feat_dict,
                time_dict=time_dict,
                batch_dict=batch_dict,
                anchor_time=anchor_time,
                filter_na=False,
            )

        right = right_mask = None
        if isinstance(logical_operation.right, Condition):
            right, right_mask = self.eval_condition(
                condition=logical_operation.right,
                feat_dict=feat_dict,
                time_dict=time_dict,
                batch_dict=batch_dict,
                anchor_time=anchor_time,
                filter_na=False,
            )
        elif isinstance(logical_operation.right, LogicalOperation):
            right, right_mask = self.eval_logical_operation(
                logical_operation=logical_operation.right,
                feat_dict=feat_dict,
                time_dict=time_dict,
                batch_dict=batch_dict,
                anchor_time=anchor_time,
                filter_na=False,
            )

        out = self.eval_bool_op(left, logical_operation.op, right)

        if right_mask is not None:
            mask &= right_mask

        if filter_na:
            out = out[mask].reset_index(drop=True)

        return out, mask

    def eval_filter(
        self,
        filter: Filter,
        feat_dict: Dict[str, pd.DataFrame],
        time_dict: Dict[str, pd.Series],
        batch_dict: Dict[str, np.ndarray],
        anchor_time: pd.Series,
    ) -> np.ndarray:
        if isinstance(filter.condition, Condition):
            return self.eval_condition(
                condition=filter.condition,
                feat_dict=feat_dict,
                time_dict=time_dict,
                batch_dict=batch_dict,
                anchor_time=anchor_time,
                filter_na=False,
            )[0].to_numpy()
        else:
            assert isinstance(filter.condition, LogicalOperation)
            return self.eval_logical_operation(
                logical_operation=filter.condition,
                feat_dict=feat_dict,
                time_dict=time_dict,
                batch_dict=batch_dict,
                anchor_time=anchor_time,
                filter_na=False,
            )[0].to_numpy()

    def eval_pquery(
        self,
        query: PQueryDefinition,
        feat_dict: Dict[str, pd.DataFrame],
        time_dict: Dict[str, pd.Series],
        batch_dict: Dict[str, np.ndarray],
        anchor_time: pd.Series,
    ) -> Tuple[pd.Series, np.ndarray]:

        mask = np.ones(len(anchor_time), dtype=bool)

        if query.entity.filter is not None:
            mask &= self.eval_filter(
                filter=query.entity.filter,
                feat_dict=feat_dict,
                time_dict=time_dict,
                batch_dict=batch_dict,
                anchor_time=anchor_time,
            )

        if getattr(query, 'assuming', None) is not None:
            if isinstance(query.assuming, Condition):
                mask &= self.eval_condition(
                    condition=query.assuming,
                    feat_dict=feat_dict,
                    time_dict=time_dict,
                    batch_dict=batch_dict,
                    anchor_time=anchor_time,
                    filter_na=False,
                )[0].to_numpy()
            else:
                assert isinstance(query.assuming, LogicalOperation)
                mask &= self.eval_logical_operation(
                    logical_operation=query.assuming,
                    feat_dict=feat_dict,
                    time_dict=time_dict,
                    batch_dict=batch_dict,
                    anchor_time=anchor_time,
                    filter_na=False,
                )[0].to_numpy()

        if isinstance(query.target, Column):
            out, _mask = self.eval_column(
                column=query.target,
                feat_dict=feat_dict,
                filter_na=True,
            )
        elif isinstance(query.target, Aggregation):
            out, _mask = self.eval_aggregation(
                aggr=query.target,
                feat_dict=feat_dict,
                time_dict=time_dict,
                batch_dict=batch_dict,
                anchor_time=anchor_time,
                filter_na=True,
            )
        elif isinstance(query.target, Condition):
            out, _mask = self.eval_condition(
                condition=query.target,
                feat_dict=feat_dict,
                time_dict=time_dict,
                batch_dict=batch_dict,
                anchor_time=anchor_time,
                filter_na=True,
            )
        else:
            assert isinstance(query.target, LogicalOperation)
            out, _mask = self.eval_logical_operation(
                logical_operation=query.target,
                feat_dict=feat_dict,
                time_dict=time_dict,
                batch_dict=batch_dict,
                anchor_time=anchor_time,
                filter_na=True,
            )

        out = out[mask[_mask]]
        mask &= _mask

        return out, mask
