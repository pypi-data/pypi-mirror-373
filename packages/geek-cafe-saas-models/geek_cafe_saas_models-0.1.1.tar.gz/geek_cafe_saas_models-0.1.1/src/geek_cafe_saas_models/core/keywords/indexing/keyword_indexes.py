"""
Geek Cafe, LLC
MIT License.  See Project Root for the license information.
"""

from typing import TYPE_CHECKING
from boto3_assist.dynamodb.dynamodb_index import DynamoDBIndex, DynamoDBKey

if TYPE_CHECKING:
    from ..keyword import Keyword


class Indexes:
    pass

    def __init__(self, model: "Keyword"):
        from ..keyword import Keyword

        self.model: Keyword = model
        self._setup_indexes()

    def _setup_indexes(self):
        for setup in (self._setup_pk, self._setup_gsi1, self._setup_gsi2):
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

        # GSI: search value; find all matches across all object types
        gsi: DynamoDBIndex = DynamoDBIndex()

        gsi.name = "gsi1"
        gsi.partition_key.attribute_name = f"{gsi.name}_pk"
        gsi.partition_key.value = lambda: DynamoDBKey.build_key(
            ("tenant", self.model.tenant_id)            
        )
        gsi.sort_key.attribute_name = f"{gsi.name}_sk"
        gsi.sort_key.value = lambda: DynamoDBKey.build_key(
            (self.model.model_name, self.model.value)
            ("match", self.model.match_pk)
        )
        self.model.indexes.add_secondary(gsi)

    def _setup_gsi2(self):

        # GSI: search for a value against a specific record type 
        # e.g. user, product, blog, etc
        gsi: DynamoDBIndex = DynamoDBIndex()

        gsi.name = "gsi1"
        gsi.partition_key.attribute_name = f"{gsi.name}_pk"
        gsi.partition_key.value = lambda: DynamoDBKey.build_key(
            ("tenant", self.model.tenant_id)
            (self.model.model_name, self.model.value),
            ("match-type", self.model.match_model_name),
        )
        gsi.sort_key.attribute_name = f"{gsi.name}_sk"
        gsi.sort_key.value = lambda: DynamoDBKey.build_key(
            ("match", self.model.match_pk)
        )
        self.model.indexes.add_secondary(gsi)
