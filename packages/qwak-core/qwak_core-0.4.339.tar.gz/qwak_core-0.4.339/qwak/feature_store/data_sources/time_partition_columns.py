from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from _qwak_proto.qwak.feature_store.sources.batch_pb2 import (
    DatePartitionColumns as ProtoDatePartitionColumns,
    DayFragmentColumn as ProtoDayFragmentColumn,
    MonthFragmentColumn as ProtoMonthFragmentColumn,
    NumericColumnRepresentation as ProtoNumericColumnRepresentation,
    TextualColumnRepresentation as ProtoTextualColumnRepresentation,
    TimeFragmentedPartitionColumns as ProtoTimeFragmentedPartitionColumns,
    YearFragmentColumn as ProtoYearFragmentColumn,
)


class ColumnRepresentation(Enum):
    """
    Time fragment columns representations
        NumericColumnRepresentation:
            Year:   2020 | '2020'
            Month:  2  | '02' | '2'
            Day:    2  | '02' | '2'
        TextualColumnRepresentation:
            Month: 'Jan' | 'JANUARY' (case-insensitive)
    """

    NumericColumnRepresentation = 1
    TextualColumnRepresentation = 2

    def _to_proto(self):
        if self == ColumnRepresentation.NumericColumnRepresentation:
            res = ProtoNumericColumnRepresentation()
        elif self == ColumnRepresentation.TextualColumnRepresentation:
            res = ProtoTextualColumnRepresentation()
        else:
            raise ValueError(
                f"Unsupported ColumnRepresentation: {self.name}, supported types: {ColumnRepresentation.NumericColumnRepresentation}, {ColumnRepresentation.TextualColumnRepresentation} "
            )
        return res


class FragmentColumn(ABC):
    column_name: str
    representation: ColumnRepresentation

    def __init__(self, column_name: str, representation: ColumnRepresentation):
        if representation not in self._valid_representations:
            raise ValueError(
                f"{self.__class__.__name__} doesn't support representation: {representation}, supported types: {self._valid_representations} "
            )
        self.column_name = column_name
        self.representation = representation

    @property
    @abstractmethod
    def _valid_representations(self) -> List[ColumnRepresentation]:
        pass

    @abstractmethod
    def _to_proto(self):
        pass


class YearFragmentColumn(FragmentColumn):
    _valid_representations: List[ColumnRepresentation] = [
        ColumnRepresentation.NumericColumnRepresentation,
    ]

    def __init__(self, column_name: str, representation: ColumnRepresentation):
        super().__init__(column_name=column_name, representation=representation)

    def _to_proto(self):
        return ProtoYearFragmentColumn(
            column_name=self.column_name,
            numeric_column_representation=self.representation._to_proto(),
        )


class MonthFragmentColumn(FragmentColumn):
    _valid_representations: List[ColumnRepresentation] = [
        ColumnRepresentation.NumericColumnRepresentation,
        ColumnRepresentation.TextualColumnRepresentation,
    ]

    def __init__(self, column_name: str, representation: ColumnRepresentation):
        super().__init__(column_name=column_name, representation=representation)

    def _to_proto(self):
        proto_numeric_column_representation = None
        proto_textual_column_representation = None
        if self.representation == ColumnRepresentation.NumericColumnRepresentation:
            proto_numeric_column_representation = self.representation._to_proto()
        elif self.representation == ColumnRepresentation.TextualColumnRepresentation:
            proto_textual_column_representation = self.representation._to_proto()
        else:
            raise ValueError(
                f"{self.__class__.__name__} partition doesn't support representation: {self.representation}, supported types: {self._valid_representations} "
            )
        return ProtoMonthFragmentColumn(
            column_name=self.column_name,
            numeric_column_representation=proto_numeric_column_representation,
            textual_column_representation=proto_textual_column_representation,
        )


class DayFragmentColumn(FragmentColumn):
    _valid_representations: List[ColumnRepresentation] = [
        ColumnRepresentation.NumericColumnRepresentation
    ]

    def __init__(self, column_name: str, representation: ColumnRepresentation):
        super().__init__(column_name=column_name, representation=representation)

    def _to_proto(self):
        return ProtoDayFragmentColumn(
            column_name=self.column_name,
            numeric_column_representation=self.representation._to_proto(),
        )


@dataclass
class TimePartitionColumns(ABC):
    @abstractmethod
    def _to_proto(self):
        pass


@dataclass
class DatePartitionColumns(TimePartitionColumns):
    date_column_name: str
    date_format: str

    def _to_proto(self):
        return ProtoDatePartitionColumns(
            date_column_name=self.date_column_name,
            date_format=self.date_format,
        )


@dataclass
class TimeFragmentedPartitionColumns(TimePartitionColumns):
    year_partition_column: YearFragmentColumn
    month_partition_column: Optional[MonthFragmentColumn] = None
    day_partition_column: Optional[DayFragmentColumn] = None

    def __post_init__(self):
        if not self.month_partition_column and self.day_partition_column:
            raise ValueError(
                "If day partition column is set then month partition column must be set as well"
            )

    def _to_proto(self):
        return ProtoTimeFragmentedPartitionColumns(
            year_partition_column=self.year_partition_column._to_proto(),
            month_partition_column=(
                self.month_partition_column._to_proto()
                if self.month_partition_column
                else None
            ),
            day_partition_column=(
                self.day_partition_column._to_proto()
                if self.day_partition_column
                else None
            ),
        )
