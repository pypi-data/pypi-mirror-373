from datetime import datetime
from typing import Any

from _qwak_proto.qwak.vectors.v1.filters_pb2 import AtomicLiteral as ProtoAtomicLiteral
from qwak.utils.datetime_utils import datetime_to_pts


def transform(value: Any) -> ProtoAtomicLiteral:
    if isinstance(value, bool):
        return ProtoAtomicLiteral(bool_literal=value)
    elif isinstance(value, str):
        return ProtoAtomicLiteral(string_literal=value)
    elif isinstance(value, int):
        return ProtoAtomicLiteral(int_literal=value)
    elif isinstance(value, float):
        return ProtoAtomicLiteral(double_literal=value)
    elif isinstance(value, datetime):
        # Assuming that timestamp is a datetime
        return ProtoAtomicLiteral(timestamp_literal=datetime_to_pts(value))
    else:
        raise ValueError(f"Unsupported data type: {type(value)}")
