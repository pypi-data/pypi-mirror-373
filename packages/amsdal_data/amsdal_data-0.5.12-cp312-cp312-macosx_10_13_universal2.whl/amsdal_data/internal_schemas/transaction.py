import amsdal_glue as glue

from amsdal_data.connections.constants import PRIMARY_PARTITION_KEY
from amsdal_data.connections.constants import TRANSACTION_TABLE

transaction_schema = glue.Schema(
    name=TRANSACTION_TABLE,
    version='',
    properties=[
        glue.PropertySchema(
            name=PRIMARY_PARTITION_KEY,
            type=str,
            required=True,
        ),
        glue.PropertySchema(
            name='address',
            type=dict,
            required=False,
            default=None,
        ),
        glue.PropertySchema(
            name='label',
            type=str,
            required=False,
            default=None,
        ),
        glue.PropertySchema(
            name='tags',
            type=list,
            required=False,
            default=None,
        ),
        glue.PropertySchema(
            name='started_at',
            type=float,
            required=False,
            default=None,
        ),
        glue.PropertySchema(
            name='ended_at',
            type=float,
            required=False,
            default=None,
        ),
    ],
    constraints=[
        glue.PrimaryKeyConstraint(
            name=f'pk_{TRANSACTION_TABLE.lower()}',
            fields=[PRIMARY_PARTITION_KEY],
        ),
    ],
)
