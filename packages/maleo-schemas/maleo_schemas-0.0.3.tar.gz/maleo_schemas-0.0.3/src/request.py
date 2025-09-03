from maleo.mixins.parameter import (
    Filters,
    ListOfDataStatuses,
    Sorts,
    Search,
    UseCache,
    StatusUpdateAction,
)
from maleo.dtos.pagination import BaseFlexiblePagination, BaseStrictPagination


class ReadSingleQueryParameter(
    ListOfDataStatuses,
    UseCache,
):
    pass


class BaseReadMultipleQueryParameter(
    Sorts,
    Search,
    ListOfDataStatuses,
    Filters,
    UseCache,
):
    pass


class ReadUnpaginatedMultipleQueryParameter(
    BaseFlexiblePagination,
    BaseReadMultipleQueryParameter,
):
    pass


class ReadPaginatedMultipleQueryParameter(
    BaseStrictPagination,
    BaseReadMultipleQueryParameter,
):
    pass


class StatusUpdateQueryParameter(StatusUpdateAction):
    pass
