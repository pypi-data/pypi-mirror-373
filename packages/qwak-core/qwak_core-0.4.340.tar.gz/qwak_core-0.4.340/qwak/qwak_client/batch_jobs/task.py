from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from _qwak_proto.qwak.batch_job.v1.batch_job_service_pb2 import (
    TaskExecutionDetails as TaskExecutionDetailsProto,
)


class TaskStatus(Enum):
    UNDEFINED_BATCH_TASK_STATUS = 0
    BATCH_TASK_COMMITTED_STATUS = 1
    BATCH_TASK_PENDING_START_STATUS = 2
    BATCH_TASK_RUNNING_STATUS = 3
    BATCH_TASK_FINISHED_STATUS = 4
    BATCH_TASK_FAILED_STATUS = 5
    BATCH_TASK_CANCELLED_STATUS = 6
    BATCH_TASK_TIMEOUT_STATUS = 7


@dataclass
class Task:
    task_id: str = field(default=None)
    task_status: TaskStatus = field(default=TaskStatus.UNDEFINED_BATCH_TASK_STATUS)
    start_time: datetime = field(default=datetime.now())
    end_time: datetime = field(default=datetime.now())
    filename: str = field(default=None)

    @staticmethod
    def from_proto(task_execution_details_proto: TaskExecutionDetailsProto):
        return Task(
            task_id=task_execution_details_proto.task_id,
            task_status=TaskStatus(task_execution_details_proto.status),
            start_time=datetime.fromtimestamp(
                task_execution_details_proto.start_time.seconds
                + task_execution_details_proto.start_time.nanos / 1e9
            ),
            end_time=datetime.fromtimestamp(
                task_execution_details_proto.end_time.seconds
                + task_execution_details_proto.end_time.nanos / 1e9
            ),
            filename=task_execution_details_proto.filename,
        )
