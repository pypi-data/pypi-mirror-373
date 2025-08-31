from sqlalchemy.sql import func as sql_func
from sqlmodel import desc, select

from planar.routers.models import SortDirection


def build_paginated_query(
    query, filters=None, offset=None, limit=None, order_by=None, order_direction=None
):
    """
    Helper function to build paginated and filtered queries.

    Args:
        query: The base SQL query to build upon
        filters: Optional list of filter conditions, where each condition is a tuple of
                (column, operator, value). Operator should be one of:
                '==', '!=', '>', '>=', '<', '<=', 'like', 'ilike', 'in', 'not_in'
                For example: [(User.name, '==', 'John'), (User.age, '>', 18)]
                For date ranges: [(Workflow.created_at, '>=', start_date)]
        offset: Optional offset for pagination
        limit: Optional limit for pagination
        order_by: Optional field or list of fields to order by
        order_direction: Optional direction to order by
    Returns:
        Tuple of (paginated query, total count query)
        The count query is guaranteed to work with the session.exec().one() pattern
    """
    # Create a copy of the query for filtering
    filtered_query = query

    # Apply filters if provided
    if filters:
        for column, operator, value in filters:
            if value is not None:  # Skip None values
                if operator == "==" or operator == "=":
                    filtered_query = filtered_query.where(column == value)
                elif operator == "!=":
                    filtered_query = filtered_query.where(column != value)
                elif operator == ">":
                    filtered_query = filtered_query.where(column > value)
                elif operator == ">=":
                    filtered_query = filtered_query.where(column >= value)
                elif operator == "<":
                    filtered_query = filtered_query.where(column < value)
                elif operator == "<=":
                    filtered_query = filtered_query.where(column <= value)
                elif operator == "like":
                    filtered_query = filtered_query.where(column.like(value))
                elif operator == "ilike":
                    filtered_query = filtered_query.where(column.ilike(value))
                elif operator == "in":
                    filtered_query = filtered_query.where(column.in_(value))
                elif operator == "not_in":
                    filtered_query = filtered_query.where(column.not_in(value))

    # Create a total count query based on the filtered query
    # For select queries with a clear table source
    if hasattr(filtered_query, "whereclause"):
        # For standard select queries, create a count query from the same structure
        count_query = select(sql_func.count())

        # Try to determine the table to select from
        if (
            hasattr(filtered_query, "get_final_froms")
            and filtered_query.get_final_froms()
        ):
            count_query = count_query.select_from(filtered_query.get_final_froms()[0])
        elif hasattr(filtered_query, "columns") and filtered_query.columns:
            # If we can't get froms, try to extract from columns
            for col in filtered_query.columns:
                if hasattr(col, "table"):
                    count_query = count_query.select_from(col.table)
                    break

        # Apply the same where clause if it exists
        if filtered_query.whereclause is not None:
            count_query = count_query.where(filtered_query.whereclause)
    else:
        # For manually constructed queries, extract from first part of query
        # Assuming the query has a clear identifier of the table it's querying
        first_table = None

        # Try to find the table by examining the query structure
        # This is a simplified approach - adjust as needed based on your query structure
        if hasattr(query, "columns") and query.columns:
            for col in query.columns:
                if hasattr(col, "table"):
                    first_table = col.table
                    break

        # Build count query based on the table and where clause
        if first_table is not None:
            count_query = select(sql_func.count()).select_from(first_table)
            if (
                hasattr(filtered_query, "whereclause")
                and filtered_query.whereclause is not None
            ):
                count_query = count_query.where(filtered_query.whereclause)
        else:
            # If we can't determine the table, create a dummy count query that returns 0
            # This ensures we don't need fallback code in the endpoint handlers
            count_query = select(sql_func.lit(0).label("count"))

    # Apply pagination
    result_query = filtered_query

    # Apply offset if provided
    if offset is not None:
        result_query = result_query.offset(offset)

    # Apply limit if provided
    if limit is not None:
        result_query = result_query.limit(limit)

    # Apply ordering
    if order_by:
        if order_direction == SortDirection.ASC:
            result_query = result_query.order_by(order_by)
        else:
            result_query = result_query.order_by(desc(order_by))

    return result_query, count_query
