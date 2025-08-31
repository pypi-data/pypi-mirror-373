from datetime import datetime
from pydantic import BaseModel, Field
from maleo.types.base.datetime import OptionalDatetime
from maleo.types.base.float import OptionalFloat


class FromTimestamp(BaseModel):
    from_date: datetime = Field(..., description="From date")


class OptionalFromTimestamp(BaseModel):
    from_date: OptionalDatetime = Field(None, description="From date. (Optional)")


class ToTimestamp(BaseModel):
    to_date: datetime = Field(..., description="To date")


class OptionalToTimestamp(BaseModel):
    to_date: OptionalDatetime = Field(None, description="To date. (Optional)")


class ExecutionTimestamp(BaseModel):
    executed_at: datetime = Field(..., description="executed_at timestamp")


class OptionalCompletionTimestamp(BaseModel):
    completed_at: OptionalDatetime = Field(..., description="completed_at timestamp")


class RequestTimestamp(BaseModel):
    requested_at: datetime = Field(..., description="requested_at timestamp")


class ResponseTimestamp(BaseModel):
    responded_at: datetime = Field(..., description="responded_at timestamp")


class CreationTimestamp(BaseModel):
    created_at: datetime = Field(..., description="created_at timestamp")


class UpdateTimestamp(BaseModel):
    updated_at: datetime = Field(..., description="updated_at timestamp")


class OptionalDeletionTimestamp(BaseModel):
    deleted_at: OptionalDatetime = Field(None, description="deleted_at timestamp")


class OptionalRestorationTimestamp(BaseModel):
    restored_at: OptionalDatetime = Field(None, description="restored_at timestamp")


class OptionalDeactivationTimestamp(BaseModel):
    deactivated_at: OptionalDatetime = Field(
        None, description="deactivated_at timestamp"
    )


class ActivationTimestamp(BaseModel):
    activated_at: datetime = Field(..., description="activated_at timestamp")


class Duration(BaseModel):
    duration: float = Field(..., description="Duration")


class OptionalDuration(BaseModel):
    duration: OptionalFloat = Field(None, description="Duration. (Optional)")


class InferenceDuration(BaseModel):
    inference_duration: float = Field(..., description="Inference duration")


class OptionalInferenceDuration(BaseModel):
    inference_duration: OptionalFloat = Field(
        None, description="Inference duration. (Optional)"
    )
