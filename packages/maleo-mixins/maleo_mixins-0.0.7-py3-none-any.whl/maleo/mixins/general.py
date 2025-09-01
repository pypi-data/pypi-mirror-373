from enum import StrEnum
from pydantic import BaseModel, Field
from typing import Generic, Optional, TypeVar, Union
from maleo.enums.sort import Order as OrderEnum
from maleo.types.base.any import OptionalAny
from maleo.types.base.boolean import OptionalBoolean
from maleo.types.base.datetime import OptionalDatetime
from maleo.types.base.float import OptionalFloat
from maleo.types.base.integer import OptionalInteger
from maleo.types.base.string import OptionalString
from .timestamp import FromTimestamp, ToTimestamp


class StatusCode(BaseModel):
    status_code: int = Field(..., description="Status code")


class SortOrder(BaseModel):
    order: OrderEnum = Field(..., description="Sort order.")


SuccessT = TypeVar("SuccessT", bound=bool)


class Success(BaseModel, Generic[SuccessT]):
    success: SuccessT = Field(..., description="Success")


CodeT = TypeVar("CodeT", bound=Union[str, StrEnum])


class Code(BaseModel, Generic[CodeT]):
    code: CodeT = Field(..., description="Code")


class Message(BaseModel):
    message: str = Field(..., description="Message")


class Description(BaseModel):
    description: str = Field(..., description="Description")


class Descriptor(Description, Message, Code[CodeT], Generic[CodeT]):
    pass


OrderT = TypeVar("OrderT", bound=OptionalInteger)


class Order(BaseModel, Generic[OrderT]):
    order: OrderT = Field(..., ge=1, description="Order")


class Key(BaseModel):
    key: str = Field(..., description="Key")


LevelT = TypeVar("LevelT", bound=Optional[StrEnum])


class Level(BaseModel, Generic[LevelT]):
    level: LevelT = Field(..., description="Level")


class Name(BaseModel):
    name: str = Field(..., description="Name")


NoteT = TypeVar("NoteT", bound=OptionalString)


class Note(BaseModel, Generic[NoteT]):
    note: NoteT = Field(..., description="Note")


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


OrganizationIdT = TypeVar("OrganizationIdT", bound=OptionalInteger)


class OrganizationId(BaseModel, Generic[OrganizationIdT]):
    organization_id: OrganizationIdT = Field(..., ge=1, description="Organization's ID")


ParentIdT = TypeVar("ParentIdT", bound=OptionalInteger)


class ParentId(BaseModel, Generic[ParentIdT]):
    parent_id: ParentIdT = Field(..., ge=1, description="Parent's ID")


UserIdT = TypeVar("UserIdT", bound=OptionalInteger)


class UserId(BaseModel, Generic[UserIdT]):
    user_id: UserIdT = Field(..., ge=1, description="User's ID")


AgeT = TypeVar("AgeT", float, int, OptionalFloat, OptionalInteger)


class Age(BaseModel, Generic[AgeT]):
    age: AgeT = Field(..., ge=0, description="Age")


class DateFilter(
    ToTimestamp[OptionalDatetime],
    FromTimestamp[OptionalDatetime],
    Name,
):
    pass


class SortColumn(
    SortOrder,
    Name,
):
    pass
