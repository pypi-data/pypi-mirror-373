from typing import Any
from typing import Self

from amsdal_utils.models.data_models.address import Address
from pydantic import BaseModel
from pydantic import Field

from amsdal_data.enums import ModifyOperation


class TransactionContext(BaseModel):
    """
    Represents the context of a transaction, including its address, method name, execution location, arguments,
        return value, changes, and parent context.

    Attributes:
        address (Address): The address associated with the transaction.
        method_name (str): The name of the method being executed.
        execution_location (str): The location where the transaction is executed.
        arguments (dict[str, Any] | None): The arguments passed to the method.
        return_value (Any | None): The return value of the method.
        changes (list[tuple[ModifyOperation, Address, dict[str, Any]]]): The list of changes made during the transaction
        parent (Optional[TransactionContext]): The parent transaction context, if any.
    """

    address: Address
    method_name: str
    execution_location: str
    arguments: dict[str, Any] | None = None
    return_value: Any | None = None
    changes: list[tuple[ModifyOperation, Address, dict[str, Any]]] = Field(default_factory=list)
    parent: Self | None = None

    @property
    def is_top_level(self) -> bool:
        return self.parent is None
