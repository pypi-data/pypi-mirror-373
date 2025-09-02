from contextlib import suppress

from amsdal_data.test_utils.constants import PG_TEST_HOST
from amsdal_data.test_utils.constants import PG_TEST_PASSWORD
from amsdal_data.test_utils.constants import PG_TEST_PORT
from amsdal_data.test_utils.constants import PG_TEST_USER


def create_postgres_database(database: str) -> None:
    import psycopg

    conn = psycopg.connect(
        host=PG_TEST_HOST,
        port=PG_TEST_PORT,
        user=PG_TEST_USER,
        password=PG_TEST_PASSWORD,
        autocommit=True,
    )
    cur = conn.cursor()

    with suppress(psycopg.errors.DuplicateDatabase):
        cur.execute(f'CREATE DATABASE "{database}"')

    cur.close()
    conn.close()


def drop_postgres_database(database: str) -> None:
    import psycopg

    conn = psycopg.connect(
        host=PG_TEST_HOST,
        port=PG_TEST_PORT,
        user=PG_TEST_USER,
        password=PG_TEST_PASSWORD,
        autocommit=True,
    )
    cur = conn.cursor()

    with suppress(psycopg.errors.DuplicateDatabase):
        cur.execute(f'DROP DATABASE "{database}"')

    cur.close()
    conn.close()


def create_postgres_extension(database: str, extension: str) -> None:
    import psycopg

    conn = psycopg.connect(
        host=PG_TEST_HOST,
        port=PG_TEST_PORT,
        user=PG_TEST_USER,
        password=PG_TEST_PASSWORD,
        dbname=database,
        autocommit=True,
    )

    conn.execute(f'CREATE EXTENSION IF NOT EXISTS {extension};')
    conn.close()
