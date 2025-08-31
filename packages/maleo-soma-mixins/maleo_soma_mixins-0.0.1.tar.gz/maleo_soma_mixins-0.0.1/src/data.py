from pydantic import BaseModel, Field
from uuid import UUID
from maleo.soma.enums.status import DataStatus as DataStatusEnum
from .timestamp import (
    CreationTimestamp,
    UpdateTimestamp,
    ActivationTimestamp,
    OptionalDeactivationTimestamp,
    OptionalRestorationTimestamp,
    OptionalDeletionTimestamp,
)


class DataIdentifier(BaseModel):
    id: int = Field(..., ge=1, description="Data's ID, must be >= 1.")
    uuid: UUID = Field(..., description="Data's UUID.")


class DataStatus(BaseModel):
    status: DataStatusEnum = Field(..., description="Data's status")


class DataLifecycleTimestamp(UpdateTimestamp, CreationTimestamp):
    pass


class DataStatusTimestamp(
    OptionalDeletionTimestamp,
    OptionalRestorationTimestamp,
    OptionalDeactivationTimestamp,
    ActivationTimestamp,
):
    pass


class DataTimestamp(DataStatusTimestamp, DataLifecycleTimestamp):
    pass
