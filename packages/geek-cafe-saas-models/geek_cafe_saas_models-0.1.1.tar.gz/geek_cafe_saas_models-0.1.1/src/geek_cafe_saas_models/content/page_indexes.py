from typing import TYPE_CHECKING
from boto3_assist.dynamodb.dynamodb_index import DynamoDBIndex, DynamoDBKey

if TYPE_CHECKING:
    from .page import Page



class Indexes:
    pass
    def __init__(self, model: "Page"):
        from .page import Page
        self.model: Page = model
        self._setup_indexes()
    
    def _setup_indexes(self):
        for setup in (self._setup_pk, self._setup_gsi1):
            setup()

   
    def _setup_pk(self):
        primary: DynamoDBIndex = DynamoDBIndex()
        primary.name = "primary"
        primary.partition_key.attribute_name = "pk"
        primary.partition_key.value = lambda: DynamoDBKey.build_key(
            ("site", self.model.site_id), ("pages", None)
        )

        primary.sort_key.attribute_name = "sk"
        primary.sort_key.value = lambda: DynamoDBKey.build_key(("page", self.model.slug))
        self.model.indexes.add_primary(primary)


    def _setup_gsi1(self):
        
        gsi: DynamoDBIndex = DynamoDBIndex()
        gsi.name = "gsi1"
        gsi.partition_key.attribute_name = f"{gsi.name}_pk"
        gsi.partition_key.value = lambda: DynamoDBKey.build_key(("site", self.model.site_id))
        gsi.sort_key.attribute_name = f"{gsi.name}_sk"
        gsi.sort_key.value = lambda: DynamoDBKey.build_key(
            ("page-expires", self.model.expires_sk_friendly)
        )
        self.model.indexes.add_secondary(gsi)

   
    

    
        