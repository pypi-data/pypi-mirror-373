from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from _qwak_proto.qwak.vectors.v1.filters_pb2 import (
    And as ProtoAnd,
    AtomicLiteral as ProtoAtomicLiteral,
    Equal as ProtoEqual,
    Filter as ProtoFilter,
    GreaterThan as ProtoGreaterThan,
    GreaterThanEqual as ProtoGreaterThanEqual,
    IsNotNull as ProtoIsNotNull,
    IsNull as ProtoIsNull,
    LessThan as ProtoLessThan,
    LessThanEqual as ProtoLessThanEqual,
    Like as ProtoLike,
    NotEqual as ProtoNotEqual,
    Or as ProtoOr,
)
from google.protobuf.json_format import MessageToDict, ParseDict
from qwak.vector_store.utils.filter_utils import transform


class Filter(ABC):
    """Abstract base class for filter objects."""

    def And(self, other):
        """Logical AND operation with another filter.

        Usage Example:
        ```
        filter1 = Equal("age", 30)
        filter2 = GreaterThan("score", 90)
        combined_filter = filter1.And(filter2)
        ```
        """
        return And(self, other)

    def Or(self, other):
        """Logical OR operation with another filter.

        Usage Example:
        ```
        filter1 = Equal("age", 30)
        filter2 = GreaterThan("score", 90)
        combined_filter = filter1.Or(filter2)
        ```
        """
        return Or(self, other)

    @abstractmethod
    def _to_proto(self):
        """Convert the filter to a protobuf representation."""
        pass


@dataclass
class And(Filter):
    """Logical And operation with another filter.

    Usage Example:
    ```
    filter1 = Equal("age", 30)
    filter2 = GreaterThan("score", 90)
    combined_filter = And(left=filter1, right=filter2)
    ```
    """

    left: Filter
    right: Filter

    def _to_proto(self):
        proto_filter = ProtoFilter()
        proto_filter_dict = MessageToDict(proto_filter)
        proto_and_dict = MessageToDict(
            ProtoAnd(left=self.left._to_proto(), right=self.right._to_proto())
        )
        proto_filter_dict["and"] = proto_and_dict
        return ParseDict(proto_filter_dict, proto_filter, ignore_unknown_fields=True)


@dataclass
class Or(Filter):
    """Logical OR operation with another filter.

    Usage Example:
    ```
    filter1 = Equal("age", 30)
    filter2 = GreaterThan("score", 90)
    combined_filter = Or(left=filter1, right=filter2)
    ```
    """

    left: Filter
    right: Filter

    def _to_proto(self):
        proto_filter = ProtoFilter()
        proto_filter_dict = MessageToDict(proto_filter)
        proto_or_dict = MessageToDict(
            ProtoOr(left=self.left._to_proto(), right=self.right._to_proto())
        )
        proto_filter_dict["or"] = proto_or_dict
        return ParseDict(proto_filter_dict, proto_filter, ignore_unknown_fields=True)


@dataclass
class _UnaryFilter(Filter):
    property: str
    value: Any

    def _to_proto(self):
        # Each UnaryFilter implements its own _to_proto
        pass


class Equal(_UnaryFilter):
    """Equal operation.

    Usage Example:
    ```
    filter = Equal(property="age", value=30)
    ```
    """

    def _to_proto(self):
        atomic_literal: ProtoAtomicLiteral = transform(value=self.value)
        return ProtoFilter(eq=ProtoEqual(property=self.property, value=atomic_literal))


class NotEqual(_UnaryFilter):
    """NotEqual operation.

    Usage Example:
    ```
    filter = NotEqual(property="age", value=30)
    ```
    """

    def _to_proto(self):
        atomic_literal: ProtoAtomicLiteral = transform(value=self.value)
        return ProtoFilter(
            ne=ProtoNotEqual(property=self.property, value=atomic_literal)
        )


class LessThanEqual(_UnaryFilter):
    """LessThanEqual operation.

    Usage Example:
    ```
    filter = LessThanEqual(property="age", value=30)
    ```
    """

    def _to_proto(self):
        atomic_literal: ProtoAtomicLiteral = transform(value=self.value)
        return ProtoFilter(
            lte=ProtoLessThanEqual(property=self.property, value=atomic_literal)
        )


class LessThan(_UnaryFilter):
    """LessThan operation.

    Usage Example:
    ```
    filter = LessThan(property="age", value=30)
    ```
    """

    def _to_proto(self):
        atomic_literal: ProtoAtomicLiteral = transform(value=self.value)
        return ProtoFilter(
            lt=ProtoLessThan(property=self.property, value=atomic_literal)
        )


class GreaterThanEqual(_UnaryFilter):
    """GreaterThanEqual operation.

    Usage Example:
    ```
    filter = GreaterThanEqual(property="age", value=30)
    ```
    """

    def _to_proto(self):
        atomic_literal: ProtoAtomicLiteral = transform(value=self.value)
        return ProtoFilter(
            gte=ProtoGreaterThanEqual(property=self.property, value=atomic_literal)
        )


class GreaterThan(_UnaryFilter):
    """GreaterThan operation.

    Usage Example:
    ```
    filter = GreaterThan(property="age", value=30)
    ```
    """

    def _to_proto(self):
        atomic_literal: ProtoAtomicLiteral = transform(value=self.value)
        return ProtoFilter(
            gt=ProtoGreaterThan(property=self.property, value=atomic_literal)
        )


@dataclass
class Like(Filter):
    """Like operation.

    Usage Example:
    ```
    filter = Like(property="name", pattern="Tal")
    ```
    """

    property: str
    pattern: str

    def _to_proto(self):
        return ProtoFilter(like=ProtoLike(property=self.property, pattern=self.pattern))


@dataclass
class IsNull(Filter):
    """IsNull operation.

    Usage Example:
    ```
    filter = IsNull(property="zipcode)
    ```
    """

    property: str

    def _to_proto(self):
        return ProtoFilter(is_null=ProtoIsNull(property=self.property))


@dataclass
class IsNotNull(Filter):
    """IsNotNull operation.

    Usage Example:
    ```
    filter = IsNotNull(property="zipcode)
    ```
    """

    property: str

    def _to_proto(self):
        return ProtoFilter(is_not_null=ProtoIsNotNull(property=self.property))


@dataclass
class Property:
    """Represents a property for building filter conditions."""

    name: str

    def gt(self, value: Any):
        """Create a GreaterThan filter for this property.

        Usage Example:
        ```
        filter = Property("age").gt(30)
        ```
        """
        return GreaterThan(self.name, value)

    def gte(self, value: Any):
        """Create a GreaterThanEqual filter for this property.

        Usage Example:
        ```
        filter = Property("score").gte(90)
        ```
        """
        return GreaterThanEqual(self.name, value)

    def lt(self, value: Any):
        """Create a LessThan filter for this property.

        Usage Example:
        ```
        filter = Property("age").lt(30)
        ```
        """
        return LessThan(self.name, value)

    def lte(self, value: Any):
        """Create a LessThanEqual filter for this property.

        Usage Example:
        ```
        filter = Property("score").lte(90)
        ```
        """
        return LessThanEqual(self.name, value)

    def eq(self, value: Any):
        """Create an Equal filter for this property.

        Usage Example:
        ```
        filter = Property("score").eq(90)
        ```
        """
        return Equal(self.name, value)

    def ne(self, value: Any):
        """Create an NotEqual filter for this property.

        Usage Example:
        ```
        filter = Property("age").ne(30)
        ```
        """
        return NotEqual(self.name, value)

    def is_null(self):
        """Create an IsNull filter for this property.

        Usage Example:
        ```
        filter = Property("zipcode").is_null()
        ```
        """
        return IsNull(self.name)

    def is_not_null(self):
        """Create an IsNotNull filter for this property.

        Usage Example:
        ```
        filter = Property("zipcode").is_not_null()
        ```
        """
        return IsNotNull(self.name)

    def like(self, pattern: str):
        """Create a Like filter for this property.

        Usage Example:
        ```
        filter = Property("name").like("Tal")
        ```
        """
        return Like(self.name, pattern)
