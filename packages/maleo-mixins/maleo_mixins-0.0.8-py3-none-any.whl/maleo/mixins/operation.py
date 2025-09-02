from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from maleo.enums.operation import OperationType as OperationTypeEnum


class OperationIdentifier(BaseModel):
    id: UUID = Field(default_factory=uuid4, description="Operation's Id.")


class OperationSummary(BaseModel):
    summary: str = Field(..., description="Operation's summary")


class OperationType(BaseModel):
    type: OperationTypeEnum = Field(..., description="Operation's type")
