from abc import ABC, abstractmethod
from typing import Dict, Generic, Optional, Tuple, TypeVar, Union

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

TableData = TypeVar('TableData')
ColumnData = TypeVar('ColumnData')
IndexData = TypeVar('IndexData')


class PQueryBackend(Generic[TableData, ColumnData, IndexData], ABC):
    @abstractmethod
    def eval_aggregation_type(
        self,
        op: AggregationType,
        feat: Optional[ColumnData],
        batch: IndexData,
        batch_size: int,
        filter_na: bool = True,
    ) -> Tuple[ColumnData, IndexData]:
        pass

    @abstractmethod
    def eval_rel_op(
        self,
        left: ColumnData,
        op: RelOp,
        right: Union[Int, Float, Str, None],
    ) -> ColumnData:
        pass

    @abstractmethod
    def eval_member_op(
        self,
        left: ColumnData,
        op: MemberOp,
        right: Union[IntList, FloatList, StrList],
    ) -> ColumnData:
        pass

    @abstractmethod
    def eval_bool_op(
        self,
        left: ColumnData,
        op: BoolOp,
        right: Optional[ColumnData],
    ) -> ColumnData:
        pass

    @abstractmethod
    def eval_column(
        self,
        column: Column,
        feat_dict: Dict[str, TableData],
        filter_na: bool = True,
    ) -> Tuple[ColumnData, IndexData]:
        pass

    @abstractmethod
    def eval_aggregation(
        self,
        aggr: Aggregation,
        feat_dict: Dict[str, TableData],
        time_dict: Dict[str, ColumnData],
        batch_dict: Dict[str, IndexData],
        anchor_time: ColumnData,
        filter_na: bool = True,
    ) -> Tuple[ColumnData, IndexData]:
        pass

    @abstractmethod
    def eval_condition(
        self,
        condition: Condition,
        feat_dict: Dict[str, TableData],
        time_dict: Dict[str, ColumnData],
        batch_dict: Dict[str, IndexData],
        anchor_time: ColumnData,
        filter_na: bool = True,
    ) -> Tuple[ColumnData, IndexData]:
        pass

    @abstractmethod
    def eval_logical_operation(
        self,
        logical_operation: LogicalOperation,
        feat_dict: Dict[str, TableData],
        time_dict: Dict[str, ColumnData],
        batch_dict: Dict[str, IndexData],
        anchor_time: ColumnData,
        filter_na: bool = True,
    ) -> Tuple[ColumnData, IndexData]:
        pass

    @abstractmethod
    def eval_filter(
        self,
        filter: Filter,
        feat_dict: Dict[str, TableData],
        time_dict: Dict[str, ColumnData],
        batch_dict: Dict[str, IndexData],
        anchor_time: ColumnData,
    ) -> IndexData:
        pass

    @abstractmethod
    def eval_pquery(
        self,
        query: PQueryDefinition,
        feat_dict: Dict[str, TableData],
        time_dict: Dict[str, ColumnData],
        batch_dict: Dict[str, IndexData],
        anchor_time: ColumnData,
    ) -> Tuple[ColumnData, IndexData]:
        pass
