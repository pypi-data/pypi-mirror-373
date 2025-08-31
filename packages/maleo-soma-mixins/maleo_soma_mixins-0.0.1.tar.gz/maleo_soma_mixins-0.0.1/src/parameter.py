import re
import urllib.parse
from pydantic import BaseModel, Field, field_validator
from enum import StrEnum
from typing import Generic, List, Optional, TypeVar
from maleo.soma.constants.patterns import DATE_FILTER_PATTERN, SORT_COLUMN_PATTERN
from maleo.soma.constants.status import FULL_STATUSES
from maleo.soma.enums.operation import ResourceOperationStatusUpdateType
from maleo.soma.enums.sort import SortOrder
from maleo.soma.types.base.integer import OptionalListOfIntegers
from maleo.soma.types.base.string import (
    ListOfStrings,
    OptionalListOfStrings,
    OptionalString,
)
from maleo.soma.types.base.uuid import OptionalListOfUUIDs
from maleo.soma.types.enums.status import (
    ListOfDataStatuses as ListOfDataStatusesEnum,
    OptionalListOfDataStatuses as OptionalListOfDataStatusesEnum,
)
from .general import DateFilter, SortColumn


IdentifierTypeT = TypeVar("IdentifierTypeT", bound=StrEnum)


class IdentifierType(BaseModel, Generic[IdentifierTypeT]):
    identifier: IdentifierTypeT = Field(..., description="Identifier's type")


IdentifierValueT = TypeVar("IdentifierValueT")


class IdentifierValue(BaseModel, Generic[IdentifierValueT]):
    value: IdentifierValueT = Field(..., description="Identifier's value")


class IdentifierTypeValue(
    IdentifierValue[IdentifierValueT],
    IdentifierType[IdentifierTypeT],
    BaseModel,
    Generic[IdentifierTypeT, IdentifierValueT],
):
    pass


class OptionalListOfIds(BaseModel):
    ids: OptionalListOfIntegers = Field(None, description="Specific Ids")


class OptionalListOfOrganizationIds(BaseModel):
    organization_ids: OptionalListOfIntegers = Field(
        None, description="Specific Organization Ids"
    )


class OptionalListOfParentIds(BaseModel):
    parent_ids: OptionalListOfIntegers = Field(None, description="Specific Parent Ids")


class OptionalListOfUserIds(BaseModel):
    user_ids: OptionalListOfIntegers = Field(None, description="Specific User Ids")


class OptionalListOfUuids(BaseModel):
    uuids: OptionalListOfUUIDs = Field(None, description="Specific Uuids")


class Filters(BaseModel):
    filters: ListOfStrings = Field(
        [],
        description="Filters for date range, e.g. 'created_at|from::<ISO_DATETIME>|to::<ISO_DATETIME>'.",
    )

    @field_validator("filters")
    @classmethod
    def validate_date_filters(cls, values):
        if isinstance(values, list):
            decoded_values = [urllib.parse.unquote(value) for value in values]
            # * Replace space followed by 2 digits, colon, 2 digits with + and those digits
            fixed_values = []
            for value in decoded_values:
                # * Look for the pattern: space followed by 2 digits, colon, 2 digits
                fixed_value = re.sub(
                    r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+) (\d{2}:\d{2})",
                    r"\1+\2",
                    value,
                )
                fixed_values.append(fixed_value)
            final_values = [
                value for value in fixed_values if DATE_FILTER_PATTERN.match(value)
            ]
            return final_values


class DateFilters(BaseModel):
    date_filters: List[DateFilter] = Field([], description="Date filters to be applied")


class ListOfDataStatuses(BaseModel):
    statuses: ListOfDataStatusesEnum = Field(
        list(FULL_STATUSES), description="Data's statuses."
    )


class OptionalListOfDataStatuses(BaseModel):
    statuses: OptionalListOfDataStatusesEnum = Field(
        None, description="Data's statuses. (Optional)"
    )


class OptionalListOfCodes(BaseModel):
    codes: OptionalListOfStrings = Field(None, description="Specific Codes")


class OptionalListOfKeys(BaseModel):
    keys: OptionalListOfStrings = Field(None, description="Specific Keys")


class OptionalListOfNames(BaseModel):
    names: OptionalListOfStrings = Field(None, description="Specific Names")


class Search(BaseModel):
    search: OptionalString = Field(None, description="Search string.")


class Sorts(BaseModel):
    sorts: ListOfStrings = Field(
        ["id.asc"],
        description="Sorting columns in 'column_name.asc' or 'column_name.desc' format.",
    )

    @field_validator("sorts")
    @classmethod
    def validate_sorts(cls, values):
        return [value for value in values if SORT_COLUMN_PATTERN.match(value)]


class SortColumns(BaseModel):
    sort_columns: List[SortColumn] = Field(
        [SortColumn(name="id", order=SortOrder.ASC)],
        description="List of columns to be sorted",
    )


class UseCache(BaseModel):
    use_cache: bool = Field(True, description="Whether to use cache")


IncludeT = TypeVar("IncludeT", bound=StrEnum)


class Include(BaseModel, Generic[IncludeT]):
    include: Optional[List[IncludeT]] = Field(None, description="Included field(s)")


ExcludeT = TypeVar("ExcludeT", bound=StrEnum)


class Exclude(BaseModel, Generic[ExcludeT]):
    exclude: Optional[List[ExcludeT]] = Field(None, description="Excluded field(s)")


class StatusUpdateAction(BaseModel):
    action: ResourceOperationStatusUpdateType = Field(
        ..., description="Status update action"
    )
