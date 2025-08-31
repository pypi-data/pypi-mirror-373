from typing import Optional
import datetime as dt

from .._base_tenant_model import BaseTenantDBModel as BaseDBModel
from .indexing.order_indexes import Indexes

class Category(BaseDBModel):
    """
    Represents an order model
    """

    def __init__(self) -> None:
        super().__init__()        
        
        self.name: Optional[str] = None
        self.description: Optional[str] = None
            
        
        Indexes(self)

    



