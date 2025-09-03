from typing import Generic
from maleo.mixins.parameter import (
    IdentifierTypeT,
    IdentifierValueT,
    IdentifierTypeValue,
    DateFilters,
    ListOfDataStatuses,
    SortColumns,
    Search,
    UseCache,
    StatusUpdateAction,
)
from .pagination import BaseFlexiblePagination, BaseStrictPagination


class ReadSingleParameter(
    ListOfDataStatuses,
    UseCache,
    IdentifierTypeValue[IdentifierTypeT, IdentifierValueT],
    Generic[IdentifierTypeT, IdentifierValueT],
):
    pass


class BaseReadMultipleParameter(
    SortColumns,
    Search,
    ListOfDataStatuses,
    DateFilters,
    UseCache,
):
    pass


class ReadUnpaginatedMultipleParameter(
    BaseFlexiblePagination,
    BaseReadMultipleParameter,
):
    pass


class ReadPaginatedMultipleParameter(
    BaseStrictPagination,
    BaseReadMultipleParameter,
):
    pass


class StatusUpdateParameter(
    StatusUpdateAction,
    IdentifierTypeValue[IdentifierTypeT, IdentifierValueT],
    Generic[IdentifierTypeT, IdentifierValueT],
):
    pass
