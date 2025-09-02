import random
import string
from collections.abc import Iterator
from contextlib import ExitStack
from contextlib import contextmanager
from pathlib import Path

from amsdal_utils.config.data_models.amsdal_config import AmsdalConfig
from amsdal_utils.config.data_models.connection_config import ConnectionConfig
from amsdal_utils.config.data_models.repository_config import RepositoryConfig
from amsdal_utils.config.data_models.resources_config import ResourcesConfig
from amsdal_utils.config.manager import AmsdalConfigManager

from amsdal_data.aliases.db import POSTGRES_HISTORICAL_ALIAS
from amsdal_data.aliases.db import POSTGRES_HISTORICAL_ASYNC_ALIAS
from amsdal_data.aliases.db import POSTGRES_STATE_ALIAS
from amsdal_data.aliases.db import POSTGRES_STATE_ASYNC_ALIAS
from amsdal_data.aliases.db import SQLITE_ALIAS
from amsdal_data.aliases.db import SQLITE_HISTORICAL_ALIAS
from amsdal_data.aliases.db import SQLITE_HISTORICAL_ASYNC_ALIAS
from amsdal_data.aliases.db import SQLITE_STATE_ASYNC_ALIAS
from amsdal_data.connections.db_alias_map import CONNECTION_BACKEND_ALIASES
from amsdal_data.test_utils.common import temp_dir
from amsdal_data.test_utils.constants import PG_TEST_HOST
from amsdal_data.test_utils.constants import PG_TEST_PASSWORD
from amsdal_data.test_utils.constants import PG_TEST_PORT
from amsdal_data.test_utils.constants import PG_TEST_USER
from amsdal_data.test_utils.db import create_postgres_database
from amsdal_data.test_utils.db import create_postgres_extension
from amsdal_data.test_utils.db import drop_postgres_database


def build_config(
    lakehouse_backend: str,
    lakehouse_credentials: dict[str, str],
    state_backend: str | None = None,
    state_credentials: dict[str, str] | None = None,
    *,
    is_async_mode: bool = False,
) -> AmsdalConfig:
    connections = {
        'lakehouse': ConnectionConfig(
            name='lakehouse',
            backend=lakehouse_backend,
            credentials=lakehouse_credentials,
        ),
    }

    if state_backend and state_credentials is not None:
        connections['state'] = ConnectionConfig(
            name='state',
            backend=state_backend,
            credentials=state_credentials,
        )

    return AmsdalConfig(
        application_name='local',
        async_mode=is_async_mode,
        connections=connections,
        resources_config=ResourcesConfig(
            lakehouse='lakehouse',
            lock='lakehouse',
            repository=RepositoryConfig(
                default='state' if state_backend else 'lakehouse',
            ),
        ),
    )


@contextmanager
def sqlite_lakehouse_only_config(db_path: Path | None = None) -> Iterator[AmsdalConfig]:
    with ExitStack() as stack:
        _db_path = db_path if db_path else stack.enter_context(temp_dir())

        config = build_config(
            lakehouse_backend=CONNECTION_BACKEND_ALIASES[SQLITE_HISTORICAL_ALIAS],
            lakehouse_credentials={
                'db_path': f'{_db_path}/amsdal_historical.sqlite3',
            },
        )
        AmsdalConfigManager().set_config(config)

        try:
            yield config
        finally:
            AmsdalConfigManager.invalidate()


@contextmanager
def sqlite_async_lakehouse_only_config(db_path: Path | None = None) -> Iterator[AmsdalConfig]:
    with ExitStack() as stack:
        _db_path = db_path if db_path else stack.enter_context(temp_dir())

        config = build_config(
            lakehouse_backend=CONNECTION_BACKEND_ALIASES[SQLITE_HISTORICAL_ASYNC_ALIAS],
            lakehouse_credentials={
                'db_path': f'{_db_path}/amsdal_historical.sqlite3',
            },
            is_async_mode=True,
        )
        AmsdalConfigManager().set_config(config)

        try:
            yield config
        finally:
            AmsdalConfigManager.invalidate()


@contextmanager
def sqlite_config(db_path: Path | None = None) -> Iterator[AmsdalConfig]:
    with ExitStack() as stack:
        _db_path = db_path if db_path else stack.enter_context(temp_dir())

        config = build_config(
            lakehouse_backend=CONNECTION_BACKEND_ALIASES[SQLITE_HISTORICAL_ALIAS],
            lakehouse_credentials={
                'db_path': f'{_db_path}/amsdal_historical.sqlite3',
            },
            state_backend=CONNECTION_BACKEND_ALIASES[SQLITE_ALIAS],
            state_credentials={
                'db_path': f'{_db_path}/amsdal_state.sqlite3',
            },
        )
        AmsdalConfigManager().set_config(config)

        try:
            yield config
        finally:
            AmsdalConfigManager.invalidate()


@contextmanager
def sqlite_async_config(db_path: Path | None = None) -> Iterator[AmsdalConfig]:
    with ExitStack() as stack:
        _db_path = db_path if db_path else stack.enter_context(temp_dir())

        config = build_config(
            lakehouse_backend=CONNECTION_BACKEND_ALIASES[SQLITE_HISTORICAL_ASYNC_ALIAS],
            lakehouse_credentials={
                'db_path': f'{_db_path}/amsdal_historical.sqlite3',
            },
            state_backend=CONNECTION_BACKEND_ALIASES[SQLITE_STATE_ASYNC_ALIAS],
            state_credentials={
                'db_path': f'{_db_path}/amsdal_state.sqlite3',
            },
            is_async_mode=True,
        )
        AmsdalConfigManager().set_config(config)

        try:
            yield config
        finally:
            AmsdalConfigManager.invalidate()


@contextmanager
def postgres_config(
    lakehouse_database: str | None = None,
    state_database: str | None = None,
    *,
    drop_database: bool = True,
) -> Iterator[AmsdalConfig]:
    lakehouse_database = lakehouse_database if lakehouse_database else ''.join(random.sample(string.ascii_letters, 16))
    state_database = state_database if state_database else ''.join(random.sample(string.ascii_letters, 16))

    config = build_config(
        lakehouse_backend=CONNECTION_BACKEND_ALIASES[POSTGRES_HISTORICAL_ALIAS],
        lakehouse_credentials={
            'dsn': f'postgresql://{PG_TEST_USER}:{PG_TEST_PASSWORD}@{PG_TEST_HOST}:{PG_TEST_PORT}/{lakehouse_database}',
        },
        state_backend=CONNECTION_BACKEND_ALIASES[POSTGRES_STATE_ALIAS],
        state_credentials={
            'dsn': f'postgresql://{PG_TEST_USER}:{PG_TEST_PASSWORD}@{PG_TEST_HOST}:{PG_TEST_PORT}/{state_database}',
        },
    )
    AmsdalConfigManager().set_config(config)
    create_postgres_database(lakehouse_database)
    create_postgres_extension(lakehouse_database, 'vector')
    create_postgres_database(state_database)
    create_postgres_extension(state_database, 'vector')

    try:
        yield config
    finally:
        AmsdalConfigManager.invalidate()

        if drop_database:
            drop_postgres_database(lakehouse_database)
            drop_postgres_database(state_database)


@contextmanager
def postgres_async_config(
    lakehouse_database: str | None = None,
    state_database: str | None = None,
    *,
    drop_database: bool = True,
) -> Iterator[AmsdalConfig]:
    lakehouse_database = lakehouse_database if lakehouse_database else ''.join(random.sample(string.ascii_letters, 16))
    state_database = state_database if state_database else ''.join(random.sample(string.ascii_letters, 16))

    config = build_config(
        lakehouse_backend=CONNECTION_BACKEND_ALIASES[POSTGRES_HISTORICAL_ASYNC_ALIAS],
        lakehouse_credentials={
            'dsn': f'postgresql://{PG_TEST_USER}:{PG_TEST_PASSWORD}@{PG_TEST_HOST}:{PG_TEST_PORT}/{lakehouse_database}',
        },
        state_backend=CONNECTION_BACKEND_ALIASES[POSTGRES_STATE_ASYNC_ALIAS],
        state_credentials={
            'dsn': f'postgresql://{PG_TEST_USER}:{PG_TEST_PASSWORD}@{PG_TEST_HOST}:{PG_TEST_PORT}/{state_database}',
        },
        is_async_mode=True,
    )
    AmsdalConfigManager().set_config(config)
    create_postgres_database(lakehouse_database)
    create_postgres_extension(lakehouse_database, 'vector')
    create_postgres_database(state_database)
    create_postgres_extension(state_database, 'vector')

    try:
        yield config
    finally:
        AmsdalConfigManager.invalidate()

        if drop_database:
            drop_postgres_database(lakehouse_database)
            drop_postgres_database(state_database)


@contextmanager
def postgres_lakehouse_only_config(
    lakehouse_database: str | None = None,
    *,
    drop_database: bool = True,
) -> Iterator[AmsdalConfig]:
    lakehouse_database = lakehouse_database if lakehouse_database else ''.join(random.sample(string.ascii_letters, 16))

    config = build_config(
        lakehouse_backend=CONNECTION_BACKEND_ALIASES[POSTGRES_HISTORICAL_ALIAS],
        lakehouse_credentials={
            'dsn': f'postgresql://{PG_TEST_USER}:{PG_TEST_PASSWORD}@{PG_TEST_HOST}:{PG_TEST_PORT}/{lakehouse_database}',
        },
    )
    AmsdalConfigManager().set_config(config)
    create_postgres_database(lakehouse_database)
    create_postgres_extension(lakehouse_database, 'vector')

    try:
        yield config
    finally:
        AmsdalConfigManager.invalidate()

        if drop_database:
            drop_postgres_database(lakehouse_database)


@contextmanager
def postgres_async_lakehouse_only_config(
    lakehouse_database: str | None = None,
    *,
    drop_database: bool = True,
) -> Iterator[AmsdalConfig]:
    lakehouse_database = lakehouse_database if lakehouse_database else ''.join(random.sample(string.ascii_letters, 16))

    config = build_config(
        lakehouse_backend=CONNECTION_BACKEND_ALIASES[POSTGRES_HISTORICAL_ASYNC_ALIAS],
        lakehouse_credentials={
            'dsn': f'postgresql://{PG_TEST_USER}:{PG_TEST_PASSWORD}@{PG_TEST_HOST}:{PG_TEST_PORT}/{lakehouse_database}',
        },
        is_async_mode=True,
    )
    AmsdalConfigManager().set_config(config)
    create_postgres_database(lakehouse_database)
    create_postgres_extension(lakehouse_database, 'vector')

    try:
        yield config
    finally:
        AmsdalConfigManager.invalidate()

        if drop_database:
            drop_postgres_database(lakehouse_database)
