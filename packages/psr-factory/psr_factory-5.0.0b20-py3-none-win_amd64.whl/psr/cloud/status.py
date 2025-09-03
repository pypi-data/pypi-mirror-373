# PSR Cloud. Copyright (C) PSR, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from enum import Enum


class ExecutionStatus(Enum):
    QUEUE = 0
    PENDING = 1
    RUNNING = 2
    SUCCESS = 3
    ERROR = 4
    SYNC_ERROR = 5
    WAITING_CANCEL = 6
    CANCELLED = 7
    NOT_IN_QUEUE = 8
    CANCELLED_PENDING = 9
    WAITING_MACHINE = 10
    WAITING_SPOT = 11
    SPOT_ACTIVE = 12
    SPOT_CANCELLED = 13
    SPOT_CANCELLED_PENDING = 14
    SERVER_CANCELLED = 15
    ABORTED = 16
    WAITING_STOP = 17
    STOPPED = 18
    CANCELLED_IDLE = 19
    WAITING_START = 20
    WAITING_MACHINE_ON = 21
    WAITING_ARCHITECTURE = 22
    WARNING = 23
    PARENT_CASE_FAILED = 24
    RESTART_INTERRUPTED = 27
    SPECIAL_WAITING = 30
    WAITING_UPLOAD_QUEUE = 31
    UPLOADED = 32


FAULTY_TERMINATION_STATUS = [
    ExecutionStatus.ERROR,
    ExecutionStatus.SYNC_ERROR,
    ExecutionStatus.CANCELLED,
    ExecutionStatus.NOT_IN_QUEUE,
    ExecutionStatus.ABORTED,
    ExecutionStatus.CANCELLED_IDLE,
    ExecutionStatus.RESTART_INTERRUPTED,
]

FINISHED_STATUS = FAULTY_TERMINATION_STATUS + [ExecutionStatus.SUCCESS]

STATUS_MAP_TEXT = {
    ExecutionStatus.QUEUE: "Item in the queue without machine allocations",
    ExecutionStatus.PENDING: "Waiting to turn machines on",
    ExecutionStatus.RUNNING: "Running",
    ExecutionStatus.SUCCESS: "Finished successfully",
    ExecutionStatus.ERROR: "Finished with errors",
    ExecutionStatus.SYNC_ERROR: "Finished due to lack of update request in a synchronous execution",
    ExecutionStatus.WAITING_CANCEL: "The cancellation was requested, but there is still no response from the queue processor",
    ExecutionStatus.CANCELLED: "Cancelled process",
    ExecutionStatus.NOT_IN_QUEUE: "Process is not in the queue",
    ExecutionStatus.CANCELLED_PENDING: "The cancellation process has already been called, but there is still no response from the Process Handler to complete the cancellation",
    ExecutionStatus.WAITING_MACHINE: "State where the queue is waiting for the machines to be connected to move to PENDING state",
    ExecutionStatus.WAITING_SPOT: "Waiting for the spot offer to be made",
    ExecutionStatus.SPOT_ACTIVE: "The bid is in active mode",
    ExecutionStatus.SPOT_CANCELLED: "The platform requested cancellation, but there is still no response from the Queue Processor",
    ExecutionStatus.SPOT_CANCELLED_PENDING: "The cancellation process has already been called by the server, but there is still no response from the Process Handler to complete the cancellation",
    ExecutionStatus.SERVER_CANCELLED: "Cancelled process by the server",
    ExecutionStatus.ABORTED: "The model runs more aborts due to lack of input files",
    ExecutionStatus.WAITING_STOP: "Waiting for STOP by the queue processor",
    ExecutionStatus.STOPPED: "STOP machines in the round are frozen",
    ExecutionStatus.CANCELLED_IDLE: "Cancelled after being idle",
    ExecutionStatus.WAITING_START: "Waiting for START by the queue processor",
    ExecutionStatus.WAITING_MACHINE_ON: "Waiting for machine to turn on",
    ExecutionStatus.WAITING_ARCHITECTURE: "Waiting for architecture change",
    ExecutionStatus.WARNING: "Finished with warnings",
    ExecutionStatus.PARENT_CASE_FAILED: "Parent case failed",
    ExecutionStatus.SPECIAL_WAITING: "Special Waiting",
    ExecutionStatus.WAITING_UPLOAD_QUEUE: "Waiting for uploading case",
    ExecutionStatus.UPLOADED: "Uploaded and Saved in Cloud",
}
