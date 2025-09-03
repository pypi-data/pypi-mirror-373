"""Provide connection management functions."""

import os
from typing import Literal

from airflow.models import Connection
from airflow.operators.python import PythonOperator

from airflow import settings


def create_connection_operator(
    conn_id: str,
    conn_type: Literal["postgres", "mssql"],
    **kwargs: dict,
) -> PythonOperator:
    """Create a connection if it does not exist

    :param str conn_id: the connection id
    :param Literal["postgres", "mssql"] conn_type: the connection type
    :param dict **kwargs: additional keyword arguments
    :return: a PythonOperator to create the connection
    :rtype: PythonOperator
    """

    def _create_connection():
        """Create a connection"""
        session = settings.Session()
        # Check if connection exists
        conn = session.query(Connection).filter(Connection.conn_id == conn_id).first()
        # If connection does not exist, create it
        if conn is None:
            new_conn = Connection(
                conn_id=conn_id,
                conn_type=conn_type,
                host=os.getenv("PLATFORM_DB_HOST") or "atlas",
                # FIXME - this envar needs added to the instance container app
                schema=os.getenv("PLATFORM_DB_NAME") or "airflowtest-sqlDatabase",
                login=os.getenv("PLATFORM_DB_USER"),
                password=os.getenv("PLATFORM_DB_PASSWORD"),
                port=int(
                    os.getenv(
                        "PLATFORM_DB_PORT",
                    )
                    or (5432 if conn_type == "postgres" else 1433)
                ),
            )
            session.add(new_conn)
            session.commit()
            print("Connection created.")
        else:
            print("Connection already exists.")

    return PythonOperator(
        task_id=f"create-connection-{conn_id}",
        python_callable=_create_connection,
        **kwargs,
    )
