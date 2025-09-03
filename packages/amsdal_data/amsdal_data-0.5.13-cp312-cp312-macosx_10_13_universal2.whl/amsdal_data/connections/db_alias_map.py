from amsdal_data.aliases.db import POSTGRES_HISTORICAL_ALIAS
from amsdal_data.aliases.db import POSTGRES_HISTORICAL_ASYNC_ALIAS
from amsdal_data.aliases.db import POSTGRES_STATE_ALIAS
from amsdal_data.aliases.db import POSTGRES_STATE_ASYNC_ALIAS
from amsdal_data.aliases.db import SQLITE_ALIAS
from amsdal_data.aliases.db import SQLITE_ASYNC_ALIAS
from amsdal_data.aliases.db import SQLITE_HISTORICAL_ALIAS
from amsdal_data.aliases.db import SQLITE_HISTORICAL_ASYNC_ALIAS
from amsdal_data.aliases.db import SQLITE_STATE_ALIAS
from amsdal_data.aliases.db import SQLITE_STATE_ASYNC_ALIAS

CONNECTION_BACKEND_ALIASES: dict[str, str] = {
    SQLITE_ALIAS: 'amsdal_glue.SqliteConnection',
    SQLITE_STATE_ALIAS: 'amsdal_glue.SqliteConnection',
    SQLITE_HISTORICAL_ALIAS: 'amsdal_data.connections.sqlite_historical.SqliteHistoricalConnection',
    POSTGRES_HISTORICAL_ALIAS: 'amsdal_data.connections.postgresql_historical.PostgresHistoricalConnection',
    POSTGRES_STATE_ALIAS: 'amsdal_data.connections.postgresql_state.PostgresStateConnection',
    SQLITE_HISTORICAL_ASYNC_ALIAS: 'amsdal_data.connections.async_sqlite_historical.AsyncSqliteHistoricalConnection',
    SQLITE_STATE_ASYNC_ALIAS: 'amsdal_glue.AsyncSqliteConnection',
    SQLITE_ASYNC_ALIAS: 'amsdal_glue.AsyncSqliteConnection',
    POSTGRES_STATE_ASYNC_ALIAS: 'amsdal_data.connections.postgresql_state.AsyncPostgresStateConnection',
    POSTGRES_HISTORICAL_ASYNC_ALIAS: 'amsdal_data.connections.postgresql_historical.AsyncPostgresHistoricalConnection',
}
