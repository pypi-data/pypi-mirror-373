"""
Module providing a hook to interactive with TDengine.
"""

import logging
from contextlib import closing, contextmanager
from typing import Any, Callable, Iterable, List, Mapping, Sequence, TypeVar, cast

import taos
from airflow.exceptions import AirflowException
from airflow.hooks.base import BaseHook
from airflow.sdk import Connection

T = TypeVar("T")
logger = logging.getLogger(__name__)


class TDengineHook(BaseHook):
    """Interact with TDengine."""
    conn_name_attr = "tdengine_conn_id"
    default_conn_name = "tdengine_default"
    conn_type = "tdengine"
    hook_name = "TDengine"
    schema = ""
    affected_rows = 0

    _test_connection_sql = "SELECT server_status()"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()

        if not self.conn_name_attr:
            raise AirflowException("conn_name_attr is not defined!")

        if len(args) == 1:
            setattr(self, self.conn_name_attr, args[0])
        elif self.conn_name_attr not in kwargs:
            setattr(self, self.conn_name_attr, self.default_conn_name)
        else:
            setattr(self, self.conn_name_attr, kwargs[self.conn_name_attr])

        self.connection = kwargs.pop("connection", None)

    def _get_conn_config(self, conn: Connection) -> dict:
        return {
            "host": conn.host or "localhost",
            "port": conn.port or 6030,
            "user": conn.login or "root",
            "password": conn.password or "taosdata",
            "database": conn.schema or "",
        }

    @contextmanager
    def _create_connection(self):
        """Context manager that closes the connection after user. """
        with closing(self.get_conn()) as conn:
            yield conn

    def _run_command(
        self,
        cursor: taos.TaosCursor,
        statement: str,
        parameters: Iterable | Mapping[str, Any] | None = None
    ):
        """Run a statement using an already open cursor."""
        if parameters:
            cursor.execute(statement, parameters)
        else:
            cursor.execute(statement)

        if cursor.affected_rows > 0:
            self.affected_rows = cursor.affected_rows
            self.log.debug("Row affected: %s", self.affected_rows)

    def _make_common_data_structure(self, result: T | Sequence[T]) -> tuple | list[tuple]:
        """Ensure the data returned from a SQL command is a standard tuple or list[tuple]."""
        if isinstance(result, Sequence):
            return cast(List[tuple], result)
        return cast(tuple, result)

    def get_conn_id(self) -> str:
        """Get the ID of connection."""
        return getattr(self, self.conn_name_attr)

    def get_conn(self) -> taos.TaosConnection:
        """
        Get connection to a TDengine database.

        Establishes a connection to a TDengine database
        by extracting the connection configuration from the Airflow connection.

        :return: a taos connection object
        """
        connection = self.connection or self.get_connection(self.get_conn_id())
        config = self._get_conn_config(connection)
        return taos.connect(**config)

    def run(
        self,
        statement: str,
        parameters: Iterable | Mapping[str, Any] | None = None,
        handler: Callable[[Any], T] | None = None,
    ) -> tuple | list[tuple] | None:
        """Run a command."""
        with self._create_connection() as conn:
            with closing(conn.cursor()) as cursor:
                self._run_command(cursor, statement, parameters)

                if handler is not None:
                    return self._make_common_data_structure(handler(cursor))
                return None

    def test_connection(self):
        """Test the connection using specific query."""
        status, message = False, ""

        try:
            self.run(self._test_connection_sql)
            status = True
            message = "TDengine is up & running."
        except taos.ConnectionError as e:
            message = str(e.msg)
            self.log.error(f"Connection to TDengine failed: {message}")

        return status, message


def fetch_all(cursor: taos.TaosCursor) -> list[tuple]:
    """Fetch all data from cursor."""
    return cursor.fetchall()
