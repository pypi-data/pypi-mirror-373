from datetime import datetime, timezone
from typing import Optional

from google.protobuf.timestamp_pb2 import Timestamp as ProtoTimestamp


def datetime_to_pts(dtime: Optional[datetime]) -> Optional[ProtoTimestamp]:
    """
    converts a python datetime to Protobuf Timestamp
    @param dtime: python datetime.datetime
    @return: if the input is None, returns None. else converts to proto timestamp in utc timezone
    """
    if not dtime:
        return None
    res: ProtoTimestamp = ProtoTimestamp()
    res.FromDatetime(dtime.replace(tzinfo=timezone.utc))

    return res
