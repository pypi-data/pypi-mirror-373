from datetime import datetime
from pydantic import BaseModel, Field, model_validator
from typing import Generic, Self, TypeVar
from maleo.types.base.datetime import OptionalDatetime
from maleo.types.base.float import OptionalFloat


TimestampT = TypeVar("TimestampT", bound=OptionalDatetime)


class FromTimestamp(BaseModel, Generic[TimestampT]):
    from_date: TimestampT = Field(..., description="From date")


class ToTimestamp(BaseModel, Generic[TimestampT]):
    to_date: TimestampT = Field(..., description="To date")


class ExecutionTimestamp(BaseModel, Generic[TimestampT]):
    executed_at: TimestampT = Field(..., description="executed_at timestamp")


class CompletionTimestamp(BaseModel, Generic[TimestampT]):
    completed_at: TimestampT = Field(..., description="completed_at timestamp")


class RequestTimestamp(BaseModel):
    requested_at: datetime = Field(..., description="requested_at timestamp")


class ResponseTimestamp(BaseModel):
    responded_at: datetime = Field(..., description="responded_at timestamp")


class CreationTimestamp(BaseModel):
    created_at: datetime = Field(..., description="created_at timestamp")


class UpdateTimestamp(BaseModel):
    updated_at: datetime = Field(..., description="updated_at timestamp")


class LifecycleTimestamp(
    UpdateTimestamp,
    CreationTimestamp,
):
    pass


class DeletionTimestamp(BaseModel, Generic[TimestampT]):
    deleted_at: TimestampT = Field(..., description="deleted_at timestamp")


class RestorationTimestamp(BaseModel, Generic[TimestampT]):
    restored_at: TimestampT = Field(..., description="restored_at timestamp")


class DeactivationTimestamp(BaseModel, Generic[TimestampT]):
    deactivated_at: TimestampT = Field(..., description="deactivated_at timestamp")


class ActivationTimestamp(BaseModel, Generic[TimestampT]):
    activated_at: TimestampT = Field(..., description="activated_at timestamp")


class StatusTimestamp(
    ActivationTimestamp, DeactivationTimestamp, RestorationTimestamp, DeletionTimestamp
):
    pass


DurationT = TypeVar("DurationT", bound=OptionalFloat)


class Duration(BaseModel, Generic[DurationT]):
    duration: DurationT = Field(..., description="Duration")


class OperationTimestamp(
    Duration[float],
    CompletionTimestamp[OptionalDatetime],
    ExecutionTimestamp[OptionalDatetime],
):
    duration: float = Field(0.0, ge=0.0, description="Duration")

    @model_validator(mode="after")
    def calculate_duration(self) -> Self:
        if (
            self.completed_at is not None
            and self.executed_at is not None
            and self.duration == 0
        ):
            self.duration = (self.completed_at - self.executed_at).total_seconds()
        return self


class InferenceDuration(BaseModel, Generic[DurationT]):
    inference_duration: DurationT = Field(..., description="Inference duration")
