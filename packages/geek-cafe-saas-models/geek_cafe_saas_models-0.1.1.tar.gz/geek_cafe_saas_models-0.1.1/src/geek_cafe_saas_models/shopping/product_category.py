from typing import Optional
import datetime as dt

from .._base_tenant_model import BaseTenantDBModel as BaseDBModel
from .indexing.product_category_indexes import Indexes

class ProductCategory(BaseDBModel):
    """
    Represents an order model
    """

    def __init__(self) -> None:
        super().__init__()        
        
        self.product_id: Optional[str] = None
        self.category_id: Optional[str] = None
        
        Indexes(self)

    



