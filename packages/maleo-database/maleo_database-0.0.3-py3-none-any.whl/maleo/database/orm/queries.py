from sqlalchemy import Column, Table
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Query, Session, aliased
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.expression import or_, asc, cast, desc
from sqlalchemy.types import DATE, String, TEXT, TIMESTAMP
from typing import Sequence, Type
from maleo.enums.sort import Order
from maleo.mixins.general import DateFilter, SortColumn
from maleo.types.base.any import OptionalAny
from maleo.types.base.boolean import OptionalBoolean
from maleo.types.base.integer import OptionalListOfIntegers
from maleo.types.base.string import OptionalListOfStrings, OptionalString
from maleo.types.enums.status import OptionalListOfDataStatuses


def filter_column(
    query: Query,
    table: Type[DeclarativeMeta],
    column: str,
    value: OptionalAny = None,
    include_null: bool = False,
) -> Query:
    column_attr = getattr(table, column, None)
    if column_attr is None or not isinstance(column_attr, InstrumentedAttribute):
        return query

    value_filters = []
    if value is not None:
        value_filters.extend([column_attr == val for val in value])

    if value_filters:
        if include_null:
            value_filters.append(column_attr.is_(None))
        query = query.filter(or_(*value_filters))

    return query


def filter_ids(
    query: Query,
    table: Type[DeclarativeMeta],
    column: str,
    ids: OptionalListOfIntegers = None,
    include_null: bool = False,
) -> Query:
    column_attr = getattr(table, column, None)
    if column_attr is None or not isinstance(column_attr, InstrumentedAttribute):
        return query

    id_filters = []
    if ids is not None:
        id_filters.extend([column_attr == id for id in ids])

    if id_filters:
        if include_null:
            id_filters.append(column_attr.is_(None))
        query = query.filter(or_(*id_filters))

    return query


def filter_timestamps(
    query: Query,
    table: Type[DeclarativeMeta],  # type: ignore
    date_filters: Sequence[DateFilter],
) -> Query:
    if date_filters and len(date_filters) > 0:
        for date_filter in date_filters:
            try:
                table: Table = table.__table__  # type: ignore
                column: Column = table.columns[date_filter.name]
                column_attr: InstrumentedAttribute = getattr(table, date_filter.name)
                if isinstance(column.type, (TIMESTAMP, DATE)):
                    if date_filter.from_date and date_filter.to_date:
                        query = query.filter(
                            column_attr.between(
                                date_filter.from_date, date_filter.to_date
                            )
                        )
                    elif date_filter.from_date:
                        query = query.filter(column_attr >= date_filter.from_date)
                    elif date_filter.to_date:
                        query = query.filter(column_attr <= date_filter.to_date)
            except KeyError:
                continue
    return query


def filter_statuses(
    query: Query,
    table: Type[DeclarativeMeta],
    statuses: OptionalListOfDataStatuses,
) -> Query:
    if statuses is not None:
        status_filters = [table.status == status for status in statuses]  # type: ignore
        query = query.filter(or_(*status_filters))
    return query


def filter_is_root(
    query: Query,
    table: Type[DeclarativeMeta],
    parent_column: str = "parent_id",
    is_root: OptionalBoolean = None,
) -> Query:
    parent_attr = getattr(table, parent_column, None)
    if parent_attr is None or not isinstance(parent_attr, InstrumentedAttribute):
        return query
    if is_root is not None:
        query = query.filter(
            parent_attr.is_(None) if is_root else parent_attr.is_not(None)
        )
    return query


def filter_is_parent(
    session: Session,
    query: Query,
    table: Type[DeclarativeMeta],
    id_column: str = "id",
    parent_column: str = "parent_id",
    is_parent: OptionalBoolean = None,
) -> Query:
    id_attr = getattr(table, id_column, None)
    if id_attr is None or not isinstance(id_attr, InstrumentedAttribute):
        return query
    parent_attr = getattr(table, parent_column, None)
    if parent_attr is None or not isinstance(parent_attr, InstrumentedAttribute):
        return query
    if is_parent is not None:
        child_table = aliased(table)
        child_parent_attr = getattr(child_table, parent_column)
        subq = session.query(child_table).filter(child_parent_attr == id_attr).exists()
        query = query.filter(subq if is_parent else ~subq)
    return query


def filter_is_child(
    query: Query,
    table: Type[DeclarativeMeta],
    parent_column: str = "parent_id",
    is_child: OptionalBoolean = None,
) -> Query:
    parent_attr = getattr(table, parent_column, None)
    if parent_attr is None or not isinstance(parent_attr, InstrumentedAttribute):
        return query
    if is_child is not None:
        query = query.filter(
            parent_attr.is_not(None) if is_child else parent_attr.is_(None)
        )
    return query


def filter_is_leaf(
    session: Session,
    query: Query,
    table: Type[DeclarativeMeta],
    id_column: str = "id",
    parent_column: str = "parent_id",
    is_leaf: OptionalBoolean = None,
) -> Query:
    id_attr = getattr(table, id_column, None)
    if id_attr is None or not isinstance(id_attr, InstrumentedAttribute):
        return query
    parent_attr = getattr(table, parent_column, None)
    if parent_attr is None or not isinstance(parent_attr, InstrumentedAttribute):
        return query
    if is_leaf is not None:
        child_table = aliased(table)
        child_parent_attr = getattr(child_table, parent_column)
        subq = session.query(child_table).filter(child_parent_attr == id_attr).exists()
        query = query.filter(~subq if is_leaf else subq)
    return query


def search(
    query: Query,
    table: Type[DeclarativeMeta],
    search: OptionalString = None,
    columns: OptionalListOfStrings = None,
) -> Query:
    if search is None:
        return query

    search_term = f"%{search}%"
    sqla_table: Table = table.__table__  # type: ignore
    search_filters = []

    for name, attr in vars(table).items():
        # Only consider InstrumentedAttribute (mapped columns)
        if not isinstance(attr, InstrumentedAttribute):
            continue

        try:
            column: Column = sqla_table.columns[name]
        except KeyError:
            continue

        # Skip columns not in the user-provided list
        if columns is not None and name not in columns:
            continue

        # Only allow string/TEXT columns
        if isinstance(column.type, (String, TEXT)):
            search_filters.append(cast(attr, TEXT).ilike(search_term))

    if search_filters:
        query = query.filter(or_(*search_filters))

    return query


def sort(
    query: Query,
    table: Type[DeclarativeMeta],
    sort_columns: Sequence[SortColumn],
) -> Query:
    for sort_column in sort_columns:
        try:
            sort_col = getattr(table, sort_column.name)
            sort_col = (
                asc(sort_col) if sort_column.order is Order.ASC else desc(sort_col)
            )
            query = query.order_by(sort_col)
        except AttributeError:
            continue
    return query


def paginate(query: Query, page: int, limit: int) -> Query:
    offset: int = int((page - 1) * limit)  # Calculate offset based on page
    query = query.limit(limit=limit).offset(offset=offset)
    return query
