"""
Geek Cafe, LLC
MIT License.  See Project Root for the license information.
"""

from typing import TYPE_CHECKING

from boto3_assist.dynamodb.dynamodb_index import DynamoDBIndex, DynamoDBKey

if TYPE_CHECKING:
    from ..relationship import Relationship


class Indexes:
    pass

    def __init__(self, model: "Relationship"):
        from ..relationship import Relationship

        self.model: Relationship = model
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
        gsi = DynamoDBIndex()
        gsi.name = "gsi1"
        gsi.partition_key.attribute_name = "gsi1_pk"
        gsi.partition_key.value = lambda: DynamoDBKey.build_key(
            ("tenant", self.model.tenant_id),
            ("user", self.model.user_id),
        )
        gsi.sort_key.attribute_name = "gsi1_sk"
        gsi.sort_key.value = lambda: DynamoDBKey.build_key(
            ("xref_type", self.model._xref_type),
            ("access", self.model.type),
            ("xref_pk", self.model._xref_pk),
        )
        self.model.indexes.add_secondary(gsi)

    def _setup_gsi2(self):
        gsi = DynamoDBIndex()
        gsi.name = "gsi2"
        gsi.partition_key.attribute_name = "gsi2_pk"
        gsi.partition_key.value = lambda: DynamoDBKey.build_key(
            ("tenant", self.model.tenant_id),
            ("asset", self.model._xref_pk),
        )
        gsi.sort_key.attribute_name = "gsi2_sk"
        gsi.sort_key.value = lambda: DynamoDBKey.build_key(
            ("xref_type", self.model._xref_type),
            ("access", self.model.type),
            ("user", self.model.user_id),
        )
        self.model.indexes.add_secondary(gsi)


    # def _setup_gsi1(self):
    #     """
    #     GSI: Get's all items of a specific type for a tenant
    #     optionally limits by (in this order):
    #         - type
    #         - user
    #         - access (assigned, owned)
    #         - specific item
    #     """
    #     # GSI: returns a tree of nodes, in order by depth and name
    #     gsi: DynamoDBIndex = DynamoDBIndex()
        
    #     gsi.name = "gsi1"
    #     gsi.partition_key.attribute_name = f"{gsi.name}_pk"
    #     gsi.partition_key.value = lambda: DynamoDBKey.build_key(
    #         ("tenant", self.model.tenant_id),
    #     )
    #     gsi.sort_key.attribute_name = f"{gsi.name}_sk"
    #     # sort order
    #     gsi.sort_key.value = lambda: DynamoDBKey.build_key(
    #         ("xref_type", self.model.xref_type),
    #         ("user", self.model.user_id),            
    #         ("access", self.model.type),                        
    #         ("xref_pk", self.model.xref_pk),
            
    #     )

    #     self.model.indexes.add_secondary(gsi)
