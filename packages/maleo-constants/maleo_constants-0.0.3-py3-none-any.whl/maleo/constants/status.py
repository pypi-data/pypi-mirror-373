from typing import Mapping
from maleo.enums.status import DataStatus
from maleo.enums.operation import ResourceOperationStatusUpdateType
from maleo.types.enums.status import SequenceOfDataStatuses


STATUS_UPDATE_RULES: Mapping[
    ResourceOperationStatusUpdateType, SequenceOfDataStatuses
] = {
    ResourceOperationStatusUpdateType.DELETE: (DataStatus.INACTIVE, DataStatus.ACTIVE),
    ResourceOperationStatusUpdateType.RESTORE: (DataStatus.DELETED,),
    ResourceOperationStatusUpdateType.DEACTIVATE: (DataStatus.ACTIVE,),
    ResourceOperationStatusUpdateType.ACTIVATE: (DataStatus.INACTIVE,),
}

STATUS_UPDATE_RESULT: Mapping[ResourceOperationStatusUpdateType, DataStatus] = {
    ResourceOperationStatusUpdateType.DELETE: DataStatus.DELETED,
    ResourceOperationStatusUpdateType.RESTORE: DataStatus.ACTIVE,
    ResourceOperationStatusUpdateType.DEACTIVATE: DataStatus.INACTIVE,
    ResourceOperationStatusUpdateType.ACTIVATE: DataStatus.ACTIVE,
}

FULL_STATUSES: SequenceOfDataStatuses = (
    DataStatus.ACTIVE,
    DataStatus.INACTIVE,
    DataStatus.DELETED,
)

BASIC_STATUSES: SequenceOfDataStatuses = (
    DataStatus.ACTIVE,
    DataStatus.INACTIVE,
)
