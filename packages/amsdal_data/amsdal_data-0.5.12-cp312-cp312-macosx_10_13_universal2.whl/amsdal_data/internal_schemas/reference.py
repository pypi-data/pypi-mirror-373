import amsdal_glue as glue

from amsdal_data.connections.constants import PRIMARY_PARTITION_KEY
from amsdal_data.connections.constants import REFERENCE_TABLE

reference_schema = glue.Schema(
    name=REFERENCE_TABLE,
    version='',
    properties=[
        glue.PropertySchema(
            name=PRIMARY_PARTITION_KEY,
            type=str,
            required=True,
        ),
        glue.PropertySchema(
            name='from_address',
            type=dict,
            required=False,
            default=None,
        ),
        glue.PropertySchema(
            name='to_address',
            type=dict,
            required=False,
            default=None,
        ),
    ],
    constraints=[
        glue.PrimaryKeyConstraint(
            name=f'pk_{REFERENCE_TABLE.lower()}',
            fields=[PRIMARY_PARTITION_KEY],
        ),
    ],
)
