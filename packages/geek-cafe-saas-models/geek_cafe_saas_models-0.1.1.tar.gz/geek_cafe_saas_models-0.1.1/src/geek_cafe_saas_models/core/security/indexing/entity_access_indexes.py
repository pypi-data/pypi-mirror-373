"""
Geek Cafe, LLC
MIT License.  See Project Root for the license information.
"""

from typing import TYPE_CHECKING
from boto3_assist.dynamodb.dynamodb_index import DynamoDBIndex, DynamoDBKey

if TYPE_CHECKING:
    from ..entity_access import EntityAccess



class Indexes:
    pass
    def __init__(self, model: "EntityAccess"):
        from ..entity_access import EntityAccess
        self.model: EntityAccess = model
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
        primary.sort_key.value = lambda: DynamoDBKey.build_key((self.model.model_name, self.model.id))
        self.model.indexes.add_primary(primary)


    def _setup_gsi1(self):
        
        # GSI: filter on:
        # - owner (who owns this entity)
        # - record type (xref)        
        gsi: DynamoDBIndex = DynamoDBIndex()
        
        gsi.name = "gsi1"
        gsi.partition_key.attribute_name = f"{gsi.name}_pk"
        gsi.partition_key.value = lambda: DynamoDBKey.build_key(("owner",self.model.owner_id))
        gsi.sort_key.attribute_name = f"{gsi.name}_sk"
        gsi.sort_key.value = lambda: DynamoDBKey.build_key(        
           ("xref", self.__check_for_wild_card(self.model.xref_pk)),                   
        )
        self.model.indexes.add_secondary(gsi)

   
    def _setup_gsi2(self):
        
        # GSI: filter on:
        # - user (which is the assignee)
        # - record type (xref)
        # - owner: Optional owner of the entity
        gsi: DynamoDBIndex = DynamoDBIndex()
        
        gsi.name = "gsi2"
        gsi.partition_key.attribute_name = f"{gsi.name}_pk"
        gsi.partition_key.value = lambda: DynamoDBKey.build_key(("user",self.model.user_id))
        gsi.sort_key.attribute_name = f"{gsi.name}_sk"
        gsi.sort_key.value = lambda: DynamoDBKey.build_key(
        
           ("xref", self.model.xref_type),
           ("owner", self.model._owner_id),                   
        )
        self.model.indexes.add_secondary(gsi)

    
    
    def __check_for_wild_card(self, value):
        """
        If we have a wild card return None, which will cut 
        off the query syntax at that point, and make the search wider
        # TODO: this needs to be tested more to see if there any issues
        """
        if value == "*":
            return ""
        return value
