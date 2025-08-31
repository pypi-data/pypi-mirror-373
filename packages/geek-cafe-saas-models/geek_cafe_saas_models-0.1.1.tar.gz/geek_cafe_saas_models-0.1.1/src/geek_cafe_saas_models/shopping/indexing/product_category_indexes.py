from typing import TYPE_CHECKING
from boto3_assist.dynamodb.dynamodb_index import DynamoDBIndex, DynamoDBKey

if TYPE_CHECKING:
    from ..product_category import ProductCategory



class Indexes:
    pass
    def __init__(self, model: "ProductCategory"):
        from ..product_category import ProductCategory
        self.model: ProductCategory = model
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
        
        # GSI: all products for a given category
        gsi: DynamoDBIndex = DynamoDBIndex()
        
        gsi.name = "gsi1"
        gsi.partition_key.attribute_name = f"{gsi.name}_pk"
        gsi.partition_key.value = lambda: DynamoDBKey.build_key((self.model.model_name, self.model.category_id))
        gsi.sort_key.attribute_name = f"{gsi.name}_sk"
        gsi.sort_key.value = lambda: DynamoDBKey.build_key(
           ("product", self.model.product_id)
        )
        self.model.indexes.add_secondary(gsi)

      
    def _setup_gsi2(self):
        
        # GSI: all categories that a given product is in
        # typically a product is only in one category for SEO but often you might find it 
        # which something like this.  I would tend to use tags or keywords when doing this
        # but it's available if needed
        gsi: DynamoDBIndex = DynamoDBIndex()
        
        gsi.name = "gsi2"
        gsi.partition_key.attribute_name = f"{gsi.name}_pk"
        gsi.partition_key.value = lambda: DynamoDBKey.build_key( ("product", self.model.product_id))
        gsi.sort_key.attribute_name = f"{gsi.name}_sk"
        gsi.sort_key.value = lambda: DynamoDBKey.build_key(
           (self.model.model_name, self.model.category_id)
        )
        self.model.indexes.add_secondary(gsi)
    
        