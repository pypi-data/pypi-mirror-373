from enum import StrEnum
from pydantic import BaseModel, Field
from typing import Generic, Optional, TypeVar, Union
from maleo.enums.error import ErrorType as ErrorTypeEnum
from maleo.enums.sort import Order as OrderEnum
from maleo.types.base.any import OptionalAny
from maleo.types.base.boolean import OptionalBoolean
from maleo.types.base.integer import OptionalInteger
from maleo.types.base.string import OptionalString
from .timestamp import OptionalFromTimestamp, OptionalToTimestamp


class ErrorType(BaseModel):
    type: ErrorTypeEnum = Field(..., description="Error type")


class StatusCode(BaseModel):
    status_code: int = Field(..., description="Status code")


class SortOrder(BaseModel):
    order: OrderEnum = Field(..., description="Sort order.")


SuccessT = TypeVar("SuccessT", bound=bool)


class GenericSuccess(BaseModel, Generic[SuccessT]):
    success: SuccessT = Field(..., description="Success")


class Success(BaseModel):
    success: bool = Field(..., description="Success")


CodeT = TypeVar("CodeT", bound=Union[str, StrEnum])


class Code(BaseModel, Generic[CodeT]):
    code: CodeT = Field(..., description="Code")


class Message(BaseModel):
    message: str = Field(..., description="Message")


class Description(BaseModel):
    description: str = Field(..., description="Description")


class Descriptor(Description, Message, Code[CodeT], Generic[CodeT]):
    pass


class Order(BaseModel):
    order: int = Field(..., ge=1, description="Order")


class OptionalOrder(BaseModel):
    order: OptionalInteger = Field(None, ge=1, description="Order. (Optional)")


class Key(BaseModel):
    key: str = Field(..., description="Key")


LevelT = TypeVar("LevelT", bound=StrEnum)


class Level(BaseModel, Generic[LevelT]):
    level: LevelT = Field(..., description="Level")


class OptionalLevel(BaseModel, Generic[LevelT]):
    level: Optional[LevelT] = Field(None, description="Level")


class Name(BaseModel):
    name: str = Field(..., description="Name")


class Note(BaseModel):
    note: str = Field(..., description="Note")


class OptionalNote(BaseModel):
    note: OptionalString = Field(None, description="Note")


class IsDefault(BaseModel):
    is_default: OptionalBoolean = Field(None, description="Whether is default")


class IsRoot(BaseModel):
    is_root: OptionalBoolean = Field(None, description="Whether is root")


class IsParent(BaseModel):
    is_parent: OptionalBoolean = Field(None, description="Whether is parent")


class IsChild(BaseModel):
    is_child: OptionalBoolean = Field(None, description="Whether is child")


class IsLeaf(BaseModel):
    is_leaf: OptionalBoolean = Field(None, description="Whether is leaf")


class OptionalOther(BaseModel):
    other: OptionalAny = Field(None, description="Other. (Optional)")


class OrganizationId(BaseModel):
    organization_id: int = Field(..., ge=1, description="Organization's ID")


class OptionalOrganizationId(BaseModel):
    organization_id: OptionalInteger = Field(
        None, ge=1, description="Organization's ID. (Optional)"
    )


class ParentId(BaseModel):
    parent_id: int = Field(..., ge=1, description="Parent's ID")


class OptionalParentId(BaseModel):
    parent_id: OptionalInteger = Field(
        None, ge=1, description="Parent's ID. (Optional)"
    )


class UserId(BaseModel):
    user_id: int = Field(..., ge=1, description="User's ID")


class OptionalUserId(BaseModel):
    user_id: OptionalInteger = Field(None, ge=1, description="User's ID. (Optional)")


AgeT = TypeVar("AgeT", int, float)


class Age(BaseModel, Generic[AgeT]):
    age: AgeT = Field(..., ge=0, description="Age")


class OptionalAge(BaseModel, Generic[AgeT]):
    age: Optional[AgeT] = Field(None, ge=0, description="Age")


class DateFilter(
    OptionalToTimestamp,
    OptionalFromTimestamp,
    Name,
):
    pass


class SortColumn(
    SortOrder,
    Name,
):
    pass
