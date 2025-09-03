# mypy: disable-error-code="type-abstract"
import amsdal_glue as glue
from amsdal_glue.applications.lakehouse import LakehouseApplication
from amsdal_glue.interfaces import AsyncDataCommandService
from amsdal_glue.interfaces import AsyncDataQueryService
from amsdal_glue.interfaces import AsyncLockCommandService
from amsdal_glue.interfaces import AsyncSchemaCommandService
from amsdal_glue.interfaces import AsyncSchemaQueryService
from amsdal_glue.interfaces import AsyncTransactionCommandService
from amsdal_glue.interfaces import DataCommandService
from amsdal_glue.interfaces import DataQueryService
from amsdal_glue.interfaces import LockCommandService
from amsdal_glue.interfaces import SchemaCommandService
from amsdal_glue.interfaces import SchemaQueryService
from amsdal_glue.interfaces import TransactionCommandService
from amsdal_glue_core.containers import SubContainer
from amsdal_utils.utils.decorators import async_mode_only
from amsdal_utils.utils.decorators import sync_mode_only

from amsdal_data.transactions.manager import AmsdalAsyncTransactionManager
from amsdal_data.transactions.manager import AmsdalTransactionManager


class OperationManager:
    @sync_mode_only
    def __init__(self, lakehouse_container: SubContainer) -> None:
        self._lakehouse_container = lakehouse_container

    def query(self, statement: glue.QueryStatement) -> glue.DataResult:
        service = glue.Container.services.get(DataQueryService)
        return service.execute(
            glue.DataQueryOperation(
                query=statement,
                root_transaction_id=AmsdalTransactionManager().get_root_transaction_id(),
                transaction_id=AmsdalTransactionManager().transaction_id,
            )
        )

    def query_lakehouse(self, statement: glue.QueryStatement) -> glue.DataResult:
        with glue.Container.switch(LakehouseApplication.LAKEHOUSE_CONTAINER_NAME):
            service = self._lakehouse_container.services.get(DataQueryService)
            return service.execute(
                glue.DataQueryOperation(
                    query=statement,
                    root_transaction_id=AmsdalTransactionManager().get_root_transaction_id(),
                    transaction_id=AmsdalTransactionManager().transaction_id,
                )
            )

    def schema_query(self, filters: glue.Conditions) -> glue.SchemaResult:
        service = glue.Container.services.get(SchemaQueryService)
        return service.execute(
            glue.SchemaQueryOperation(
                filters=filters,
                root_transaction_id=AmsdalTransactionManager().get_root_transaction_id(),
                transaction_id=AmsdalTransactionManager().transaction_id,
            )
        )

    def schema_query_lakehouse(self, filters: glue.Conditions) -> glue.SchemaResult:
        with glue.Container.switch(LakehouseApplication.LAKEHOUSE_CONTAINER_NAME):
            service = self._lakehouse_container.services.get(SchemaQueryService)
            return service.execute(
                glue.SchemaQueryOperation(
                    filters=filters,
                    root_transaction_id=AmsdalTransactionManager().get_root_transaction_id(),
                    transaction_id=AmsdalTransactionManager().transaction_id,
                )
            )

    def perform_data_command(self, command: glue.DataCommand) -> glue.DataResult:
        service = glue.Container.services.get(DataCommandService)
        return service.execute(command)

    def perform_data_command_lakehouse(self, command: glue.DataCommand) -> glue.DataResult:
        with glue.Container.switch(LakehouseApplication.LAKEHOUSE_CONTAINER_NAME):
            service = self._lakehouse_container.services.get(DataCommandService)
            return service.execute(command)

    def perform_schema_command(self, command: glue.SchemaCommand) -> glue.SchemaResult:
        service = glue.Container.services.get(SchemaCommandService)
        return service.execute(command)

    def perform_schema_command_lakehouse(self, command: glue.SchemaCommand) -> glue.SchemaResult:
        with glue.Container.switch(LakehouseApplication.LAKEHOUSE_CONTAINER_NAME):
            service = self._lakehouse_container.services.get(SchemaCommandService)
            return service.execute(command)

    def perform_transaction_command(self, command: glue.TransactionCommand) -> glue.TransactionResult:
        service = glue.Container.services.get(TransactionCommandService)
        return service.execute(command)

    def perform_lock_command(self, command: glue.LockCommand) -> glue.LockResult:
        service = glue.Container.services.get(LockCommandService)
        return service.execute(command)


class AsyncOperationManager:
    @async_mode_only
    def __init__(self, lakehouse_container: SubContainer) -> None:
        self._lakehouse_container = lakehouse_container

    async def query(self, statement: glue.QueryStatement) -> glue.DataResult:
        service = glue.Container.services.get(AsyncDataQueryService)
        return await service.execute(
            glue.DataQueryOperation(
                query=statement,
                root_transaction_id=AmsdalAsyncTransactionManager().get_root_transaction_id(),
                transaction_id=AmsdalAsyncTransactionManager().transaction_id,
            )
        )

    async def query_lakehouse(self, statement: glue.QueryStatement) -> glue.DataResult:
        with glue.Container.switch(LakehouseApplication.LAKEHOUSE_CONTAINER_NAME):
            service = self._lakehouse_container.services.get(AsyncDataQueryService)
            return await service.execute(
                glue.DataQueryOperation(
                    query=statement,
                    root_transaction_id=AmsdalAsyncTransactionManager().get_root_transaction_id(),
                    transaction_id=AmsdalAsyncTransactionManager().transaction_id,
                )
            )

    async def schema_query(self, filters: glue.Conditions) -> glue.SchemaResult:
        service = glue.Container.services.get(AsyncSchemaQueryService)
        return await service.execute(
            glue.SchemaQueryOperation(
                filters=filters,
                root_transaction_id=AmsdalAsyncTransactionManager().get_root_transaction_id(),
                transaction_id=AmsdalAsyncTransactionManager().transaction_id,
            )
        )

    async def schema_query_lakehouse(self, filters: glue.Conditions) -> glue.SchemaResult:
        with glue.Container.switch(LakehouseApplication.LAKEHOUSE_CONTAINER_NAME):
            service = self._lakehouse_container.services.get(AsyncSchemaQueryService)
            return await service.execute(
                glue.SchemaQueryOperation(
                    filters=filters,
                    root_transaction_id=AmsdalAsyncTransactionManager().get_root_transaction_id(),
                    transaction_id=AmsdalAsyncTransactionManager().transaction_id,
                )
            )

    async def perform_data_command(self, command: glue.DataCommand) -> glue.DataResult:
        service = glue.Container.services.get(AsyncDataCommandService)

        return await service.execute(command)

    async def perform_data_command_lakehouse(self, command: glue.DataCommand) -> glue.DataResult:
        with glue.Container.switch(LakehouseApplication.LAKEHOUSE_CONTAINER_NAME):
            service = self._lakehouse_container.services.get(AsyncDataCommandService)
            return await service.execute(command)

    async def perform_schema_command(self, command: glue.SchemaCommand) -> glue.SchemaResult:
        service = glue.Container.services.get(AsyncSchemaCommandService)
        return await service.execute(command)

    async def perform_schema_command_lakehouse(self, command: glue.SchemaCommand) -> glue.SchemaResult:
        with glue.Container.switch(LakehouseApplication.LAKEHOUSE_CONTAINER_NAME):
            service = self._lakehouse_container.services.get(AsyncSchemaCommandService)
            return await service.execute(command)

    async def perform_transaction_command(self, command: glue.TransactionCommand) -> glue.TransactionResult:
        service = glue.Container.services.get(AsyncTransactionCommandService)
        return await service.execute(command)

    async def perform_lock_command(self, command: glue.LockCommand) -> glue.LockResult:
        service = glue.Container.services.get(AsyncLockCommandService)
        return await service.execute(command)

    async def perform_lock_command_lakehouse(self, command: glue.LockCommand) -> glue.LockResult:
        with glue.Container.switch(LakehouseApplication.LAKEHOUSE_CONTAINER_NAME):
            service = glue.Container.services.get(AsyncLockCommandService)
            return await service.execute(command)
