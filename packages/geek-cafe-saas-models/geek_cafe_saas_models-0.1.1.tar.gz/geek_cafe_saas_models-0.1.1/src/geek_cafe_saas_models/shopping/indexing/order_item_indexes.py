from typing import TYPE_CHECKING
from boto3_assist.dynamodb.dynamodb_index import DynamoDBIndex, DynamoDBKey

if TYPE_CHECKING:
    from ..order_item import OrderItem



class Indexes:
    pass
    def __init__(self, model: "OrderItem"):
        from ..order_item import OrderItem
        self.model: OrderItem = model
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
        """
        GSI1: all line items by order
            pk: order#<order_id>
            sk: item#<item-id>
        """
        
        gsi: DynamoDBIndex = DynamoDBIndex()
        
        gsi.name = "gsi1"
        gsi.partition_key.attribute_name = f"{gsi.name}_pk"
        gsi.partition_key.value = lambda: DynamoDBKey.build_key(("order", self.model.order_id))
        gsi.sort_key.attribute_name = f"{gsi.name}_sk"
        gsi.sort_key.value = lambda: DynamoDBKey.build_key(
           ("item", self.model.id)
        )
        self.model.indexes.add_secondary(gsi)

   
    

    
        