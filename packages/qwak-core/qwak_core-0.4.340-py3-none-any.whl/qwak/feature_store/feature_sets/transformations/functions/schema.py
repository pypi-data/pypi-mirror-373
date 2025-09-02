from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


class DataType(ABC):
    @abstractmethod
    def to_ddl(self) -> str:
        pass


@dataclass
class SimpleType(DataType):
    type_name: str

    def to_ddl(self) -> str:
        return self.type_name


@dataclass
class ArrayType(DataType):
    type: DataType

    def to_ddl(self) -> str:
        return f"array<{self.type.to_ddl()}>"


class Type:
    array = ArrayType
    int = SimpleType("integer")
    long = SimpleType("long")
    string = SimpleType("string")
    double = SimpleType("double")
    decimal = SimpleType("decimal")
    float = SimpleType("float")
    boolean = SimpleType("boolean")
    timestamp = SimpleType("timestamp")
    date = SimpleType("date")


@dataclass
class Column:
    type: DataType
    name: Optional[str] = None

    def to_ddl(self) -> str:
        if self.name:
            return f"{self.name} {self.type.to_ddl()}"
        return self.type.to_ddl()


@dataclass
class Schema:
    columns: List[Column]

    def to_ddl(self) -> str:
        return ", ".join([column.to_ddl() for column in self.columns])
