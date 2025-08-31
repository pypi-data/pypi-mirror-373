"""
Geek Cafe, LLC
MIT License.  See Project Root for the license information.
"""

from typing import TYPE_CHECKING
from boto3_assist.dynamodb.dynamodb_index import DynamoDBIndex, DynamoDBKey

if TYPE_CHECKING:
    from .. import Task


class Indexes:
    pass

    def __init__(self, model: "Task"):
        from .. import Task

        self.model: Task = model
        self._setup_indexes()

    def _setup_indexes(self):
        for setup in (self._setup_pk, self._setup_gsi1):
            setup()

    def _setup_pk(self):
        primary: DynamoDBIndex = DynamoDBIndex()
        primary.name = "primary"
        primary.partition_key.attribute_name = "pk"
        primary.partition_key.value = lambda: DynamoDBKey.build_key(
            (self.model.model_name, self.model.id)
        )

        primary.sort_key.attribute_name = "sk"
        primary.sort_key.value = lambda: DynamoDBKey.build_key(
            (self.model.model_name, self.model.id)
        )
        self.model.indexes.add_primary(primary)

    def _setup_gsi1(self):

        # GSI: all task by name
        gsi: DynamoDBIndex = DynamoDBIndex()

        gsi.name = "gsi1"
        gsi.partition_key.attribute_name = f"{gsi.name}_pk"
        gsi.partition_key.value = lambda: DynamoDBKey.build_key(
            ("user", self.model.user_id)
        )
        gsi.sort_key.attribute_name = f"{gsi.name}_sk"
        gsi.sort_key.value = lambda: DynamoDBKey.build_key(            
            (self.model.model_name, "*"),
            ("name", self.model.subject)
        )
        self.model.indexes.add_secondary(gsi)

    def _setup_gsi2(self):

        # GSI: all task by name
        gsi: DynamoDBIndex = DynamoDBIndex()

        gsi.name = "gsi1"
        gsi.partition_key.attribute_name = f"{gsi.name}_pk"
        gsi.partition_key.value = lambda: DynamoDBKey.build_key(
            ("user", self.model.user_id)
        )
        gsi.sort_key.attribute_name = f"{gsi.name}_sk"
        gsi.sort_key.value = lambda: DynamoDBKey.build_key(            
            (self.model.model_name, "*"),
            ("status", self.model.status),
            ("due_ts", self.model.to_timestamp_or_none(self.model.due_date_utc))
        )
        self.model.indexes.add_secondary(gsi)