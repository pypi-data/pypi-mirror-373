"""
Geek Cafe, LLC
MIT License.  See Project Root for the license information.
"""

from typing import Optional, List

from ..._base_tenant_user_model import BaseTenantUserDBModel as BaseDBModel
from .indexing.node_indexes import Indexes


from enum import Enum

class NodeKind(str, Enum):
    CONTAINER = "container"
    LEAF = "leaf"


class Node(BaseDBModel):
    """
    Represents a Hierarchical Tree Node.  DynamoDB doesn't have joins but you can mimic them in 
    a single table design with related sort keys.  This Module helps create relationships between entities that can 
    returned in a single query.

    You can use this with categories to create sub categories, families to create family trees,
    Organizations to create Org Units, Departments, Managers, Employee relationships
    """

    def __init__(self) -> None:
        super().__init__()

        self._name: Optional[str] = None
        self.__type: Optional[NodeKind] = None
        

        # tracks what is "linked" to this entry
        self.__leaf_item_pk: Optional[str] = None
        
        

        # tree relationships
        self.__root_pk: Optional[str] = None        
        self.__parent_pk: Optional[str] = None                                                   
        self.__path: Optional[List[str]] = None  # don't use in dynamodb for sk - we could run into limits
        Indexes(self)


    @property
    def name(self) -> str:
        """
        The name of the node
        """

        if not self.serialization_in_progress():
            if not self._name:
                raise ValueError("Name is required")
            if not isinstance(self._name, str):
                raise ValueError("Name must be a string")
        return self._name
    
    @name.setter
    def name(self, value: str):
        self._name = value


    @property
    def type(self) -> NodeKind | None:
        return self.__type

    @type.setter
    def type(self, value: NodeKind | str | None):
        if isinstance(value, str):
            value = NodeKind(value)
        
        if not value and not isinstance(value, NodeKind):
            raise ValueError("Type must be a NodeKind")
        
        self.__type = value

    ## root
    @property
    def root_pk(self) -> str:
        return self.__root_pk or self.__parent_pk
    
    @root_pk.setter
    def root_pk(self, value: str):
        self.__root_pk = value

    
    ## parent
    
    @property
    def parent_pk(self) -> str:
        return self.__parent_pk or self.__root_pk
    
    @parent_pk.setter
    def parent_pk(self, value: str):
        self.__parent_pk = value

    

    
    @property
    def leaf_item_pk(self) -> str:
        return self.__leaf_item_pk
    
    @leaf_item_pk.setter
    def leaf_item_pk(self, value: str):
        self.__leaf_item_pk = value


    


    @property
    def path(self) -> List[str]:
        """
        A friendly path or slug in an array.
        This defaults to a simple [parent_name, child_name] array
        However if you are several layers deep you can override this to more levels
        [root, child, child, child]
        """
        if not self.__path:
            self.__path = [self.name]

        return self.__path
    
    @path.setter
    def path(self, value: List[str]):

        if not isinstance(value, list):
            raise ValueError("Path must be a list of strings")

        self.__path = value



    
    def is_leaf(self) -> bool:
        """Determines if the the item is a leaf or not"""
        return self.__type == NodeKind.LEAF
    
    def is_container(self) -> bool:
        """Determines if the the item is a container or not"""
        return self.__type == NodeKind.CONTAINER
