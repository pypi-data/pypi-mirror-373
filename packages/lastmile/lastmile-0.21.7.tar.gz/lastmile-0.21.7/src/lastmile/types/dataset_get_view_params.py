# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = [
    "DatasetGetViewParams",
    "Filter",
    "FilterAllOf",
    "FilterAllOfPredicate",
    "FilterAllOfPredicateNumericCriteria",
    "FilterAllOfPredicateStringCriteria",
    "FilterAllOfPredicateStringListCriteria",
    "FilterAnyOf",
    "FilterAnyOfPredicate",
    "FilterAnyOfPredicateNumericCriteria",
    "FilterAnyOfPredicateStringCriteria",
    "FilterAnyOfPredicateStringListCriteria",
]


class DatasetGetViewParams(TypedDict, total=False):
    dataset_file_id: Required[Annotated[str, PropertyInfo(alias="datasetFileId")]]
    """
    The ID of the (pinned) dataset file from which to retrieve content. Requests
    iterating over pages of results are recommended to use this pinned identifier
    after the first page in order to prevent any effects from a dataset changing
    between the queries.
    """

    dataset_id: Required[Annotated[str, PropertyInfo(alias="datasetId")]]
    """The ID of the dataset from which to retrieve content.

    When specified, gets data from the current file in the dataset.
    """

    filters: Required[Iterable[Filter]]

    after: int
    """Pagination: The index, by row-order, after which to query results."""

    get_last_page: Annotated[bool, PropertyInfo(alias="getLastPage")]

    limit: int
    """Pagination: The maximum number of results to return on this page."""

    next_page_cursor: Annotated[str, PropertyInfo(alias="nextPageCursor")]
    """A cursor for the next page in the pagination, if one exists."""

    order_by: Annotated[str, PropertyInfo(alias="orderBy")]
    """Column to order results by"""

    order_direction: Annotated[str, PropertyInfo(alias="orderDirection")]
    """Direction to order results ("asc" or "desc")"""

    previous_page_cursor: Annotated[str, PropertyInfo(alias="previousPageCursor")]
    """A cursor for the previous page in the pagination, if one exists."""

    use_datasets_service: Annotated[bool, PropertyInfo(alias="useDatasetsService")]


class FilterAllOfPredicateNumericCriteria(TypedDict, total=False):
    double_value: Required[Annotated[float, PropertyInfo(alias="doubleValue")]]

    int64_value: Required[Annotated[int, PropertyInfo(alias="int64Value")]]

    operator: Required[
        Literal[
            "OPERATOR_UNSPECIFIED",
            "OPERATOR_EQUALS",
            "OPERATOR_NOT_EQUALS",
            "OPERATOR_GREATER_THAN",
            "OPERATOR_GREATER_THAN_OR_EQUAL",
            "OPERATOR_LESS_THAN",
            "OPERATOR_LESS_THAN_OR_EQUAL",
        ]
    ]


class FilterAllOfPredicateStringCriteria(TypedDict, total=False):
    operator: Required[
        Literal[
            "OPERATOR_UNSPECIFIED",
            "OPERATOR_EQUALS",
            "OPERATOR_NOT_EQUALS",
            "OPERATOR_CONTAINS",
            "OPERATOR_STARTS_WITH",
            "OPERATOR_ENDS_WITH",
        ]
    ]

    value: Required[str]


class FilterAllOfPredicateStringListCriteria(TypedDict, total=False):
    operator: Required[Literal["OPERATOR_UNSPECIFIED", "OPERATOR_HAS_ANY", "OPERATOR_HAS_ALL", "OPERATOR_HAS_NONE"]]

    values: Required[List[str]]


class FilterAllOfPredicate(TypedDict, total=False):
    column_name: Required[Annotated[str, PropertyInfo(alias="columnName")]]

    numeric_criteria: Required[Annotated[FilterAllOfPredicateNumericCriteria, PropertyInfo(alias="numericCriteria")]]

    string_criteria: Required[Annotated[FilterAllOfPredicateStringCriteria, PropertyInfo(alias="stringCriteria")]]

    string_list_criteria: Required[
        Annotated[FilterAllOfPredicateStringListCriteria, PropertyInfo(alias="stringListCriteria")]
    ]


class FilterAllOf(TypedDict, total=False):
    predicates: Required[Iterable[FilterAllOfPredicate]]


class FilterAnyOfPredicateNumericCriteria(TypedDict, total=False):
    double_value: Required[Annotated[float, PropertyInfo(alias="doubleValue")]]

    int64_value: Required[Annotated[int, PropertyInfo(alias="int64Value")]]

    operator: Required[
        Literal[
            "OPERATOR_UNSPECIFIED",
            "OPERATOR_EQUALS",
            "OPERATOR_NOT_EQUALS",
            "OPERATOR_GREATER_THAN",
            "OPERATOR_GREATER_THAN_OR_EQUAL",
            "OPERATOR_LESS_THAN",
            "OPERATOR_LESS_THAN_OR_EQUAL",
        ]
    ]


class FilterAnyOfPredicateStringCriteria(TypedDict, total=False):
    operator: Required[
        Literal[
            "OPERATOR_UNSPECIFIED",
            "OPERATOR_EQUALS",
            "OPERATOR_NOT_EQUALS",
            "OPERATOR_CONTAINS",
            "OPERATOR_STARTS_WITH",
            "OPERATOR_ENDS_WITH",
        ]
    ]

    value: Required[str]


class FilterAnyOfPredicateStringListCriteria(TypedDict, total=False):
    operator: Required[Literal["OPERATOR_UNSPECIFIED", "OPERATOR_HAS_ANY", "OPERATOR_HAS_ALL", "OPERATOR_HAS_NONE"]]

    values: Required[List[str]]


class FilterAnyOfPredicate(TypedDict, total=False):
    column_name: Required[Annotated[str, PropertyInfo(alias="columnName")]]

    numeric_criteria: Required[Annotated[FilterAnyOfPredicateNumericCriteria, PropertyInfo(alias="numericCriteria")]]

    string_criteria: Required[Annotated[FilterAnyOfPredicateStringCriteria, PropertyInfo(alias="stringCriteria")]]

    string_list_criteria: Required[
        Annotated[FilterAnyOfPredicateStringListCriteria, PropertyInfo(alias="stringListCriteria")]
    ]


class FilterAnyOf(TypedDict, total=False):
    predicates: Required[Iterable[FilterAnyOfPredicate]]


class Filter(TypedDict, total=False):
    all_of: Required[Annotated[FilterAllOf, PropertyInfo(alias="allOf")]]

    any_of: Required[Annotated[FilterAnyOf, PropertyInfo(alias="anyOf")]]
