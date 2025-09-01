from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from _qwak_proto.qwak.batch_job.v1.batch_job_service_pb2 import (
    BatchJobDetails as BatchJobDetailsProto,
)


class ExecutionStatus(Enum):
    UNDEFINED_BATCH_JOB_STATUS = 0
    BATCH_JOB_COMMITTED_STATUS = 1
    BATCH_JOB_PENDING_STATUS = 2
    BATCH_JOB_RUNNING_STATUS = 3
    BATCH_JOB_FINISHED_STATUS = 4
    BATCH_JOB_FAILED_STATUS = 5
    BATCH_JOB_CANCELLED_STATUS = 6
    BATCH_JOB_TIMEOUT_STATUS = 7


@dataclass
class Execution:
    environment_id: str = field(default=None)
    build_id: str = field(default=None)
    execution_id: str = field(default=None)
    execution_status: ExecutionStatus = field(
        default=ExecutionStatus.UNDEFINED_BATCH_JOB_STATUS
    )
    start_time: datetime = field(default=datetime.now())
    end_time: datetime = field(default=datetime.now())
    failure_message: str = field(default=None)

    @staticmethod
    def from_proto(batch_job_details_proto: BatchJobDetailsProto):
        return Execution(
            environment_id=batch_job_details_proto.environment_id,
            build_id=batch_job_details_proto.build_id,
            execution_id=batch_job_details_proto.job_id,
            execution_status=ExecutionStatus(batch_job_details_proto.job_status),
            start_time=datetime.fromtimestamp(
                batch_job_details_proto.start_time.seconds
                + batch_job_details_proto.start_time.nanos / 1e9
            ),
            end_time=datetime.fromtimestamp(
                batch_job_details_proto.end_time.seconds
                + batch_job_details_proto.end_time.nanos / 1e9
            ),
            failure_message=batch_job_details_proto.failure_message,
        )
