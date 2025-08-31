from typing import TYPE_CHECKING
from boto3_assist.dynamodb.dynamodb_index import DynamoDBIndex, DynamoDBKey

if TYPE_CHECKING:
    from .. import Tenant



class Indexes:
    pass
    def __init__(self, model: "Tenant"):
        from .. import Tenant
        self.model: Tenant = model
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
        
        # GSI: all events by calendar date
        gsi1: DynamoDBIndex = DynamoDBIndex()
        gsi1.name = "gsi1"
        gsi1.partition_key.attribute_name = "gsi1_pk"
        gsi1.partition_key.value = lambda: DynamoDBKey.build_key((self.model.model_name, self.model.name))
        gsi1.sort_key.attribute_name = "gsi1_sk"
        gsi1.sort_key.value = lambda: DynamoDBKey.build_key(
           (self.model.model_name, self.model.name)
        )
        self.model.indexes.add_secondary(gsi1)

   