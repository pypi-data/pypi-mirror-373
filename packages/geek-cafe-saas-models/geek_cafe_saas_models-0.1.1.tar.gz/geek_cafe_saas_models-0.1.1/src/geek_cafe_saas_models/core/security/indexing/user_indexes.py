"""
Geek Cafe, LLC
MIT License.  See Project Root for the license information.
"""

from typing import TYPE_CHECKING
from boto3_assist.dynamodb.dynamodb_index import DynamoDBIndex, DynamoDBKey

if TYPE_CHECKING:
    from ..user import User



class Indexes:
    pass
    def __init__(self, model: "User"):
        from ..user import User
        self.model: User = model
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
        primary.sort_key.value = lambda: DynamoDBKey.build_key((self.model.model_name, self.model.id))
        self.model.indexes.add_primary(primary)


    def _setup_gsi1(self):
        
        # GSI: all users by email address
        gsi: DynamoDBIndex = DynamoDBIndex()
        
        gsi.name = "gsi1"
        gsi.partition_key.attribute_name = f"{gsi.name}_pk"
        gsi.partition_key.value = lambda: DynamoDBKey.build_key((self.model.model_name, "email"))
        gsi.sort_key.attribute_name = f"{gsi.name}_sk"
        gsi.sort_key.value = lambda: DynamoDBKey.build_key(
           ("email", self.model.email)
        )
        self.model.indexes.add_secondary(gsi)

   
    def _setup_gsi2(self):
        
        # GSI: all users for a specific tenant tenant
        gsi: DynamoDBIndex = DynamoDBIndex()
        gsi.name = "gsi2"
        gsi.partition_key.attribute_name = f"{gsi.name}_pk"
        gsi.partition_key.value = lambda: DynamoDBKey.build_key((self.model.model_name, "tenant"))
        gsi.sort_key.attribute_name = f"{gsi.name}_sk"
        gsi.sort_key.value = lambda: DynamoDBKey.build_key(
           ("tenant", self.model.tenant_id),
           ("last_name", self.model.last_name),
           ("first_name", self.model.first_name)
        )
        self.model.indexes.add_secondary(gsi)

    
        