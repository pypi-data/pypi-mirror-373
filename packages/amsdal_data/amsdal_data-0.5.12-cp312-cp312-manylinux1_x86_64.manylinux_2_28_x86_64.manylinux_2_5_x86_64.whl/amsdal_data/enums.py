from enum import Enum


class ModifyOperation(str, Enum):
    """
    Enum representing modify operations.

    Attributes:
        CREATE (str): Represents the create operation.
        UPDATE (str): Represents the update operation.
        DELETE (str): Represents the delete operation.
    """

    CREATE = 'create'
    UPDATE = 'update'
    DELETE = 'delete'


class CoreResource(str, Enum):
    """
    Enum representing core resources.

    Attributes:
        TRANSACTION (str): Represents the transaction resource.
        LOCK (str): Represents the lock resource.
    """

    TRANSACTION = 'transaction'
    LOCK = 'lock'
