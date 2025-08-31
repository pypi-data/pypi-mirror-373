from typing import Any, TypeVar

from ._middlewares import before_query_middlewares
from ._update_wrapper import UpdateWrapper
from .mysql._mysql_data_source import MysqlDataSource
from .mysql._reusable_mysql_connection import ReusableMysqlConnection
from .utils.random_utils import generate_random_string

T = TypeVar("T", bound=Any)


def update(
    wrapper: UpdateWrapper[T],
    conn: ReusableMysqlConnection | None = None,
    data_source: MysqlDataSource | None = None,
) -> int:
    if wrapper._where.count() == 0:
        raise ValueError("where condition is required for update operation")

    if len(wrapper._update_fields) == 0:
        raise ValueError("update fields are required")

    if data_source is None:
        raise ValueError("data_source must be provided")

    operation_id = generate_random_string("U-", 10)

    for middleware in before_query_middlewares:
        if callable(middleware):
            middleware(wrapper)

    sql, args = wrapper.build_sql()
    if conn is None:
        new_conn = data_source.get_reusable_connection()
        try:
            new_conn.acquire(operation_id=operation_id)
            new_conn.begin()
            row_affected, _ = data_source.get_executor().execute(new_conn, sql, args)
            new_conn.commit()
            return row_affected or 0
        finally:
            new_conn.release(operation_id=operation_id)
    row_affected, _ = data_source.get_executor().execute(conn, sql, args)
    return row_affected or 0
