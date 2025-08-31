from typing import Optional
import datetime as dt

from .._base_tenant_model import BaseTenantDBModel as BaseDBModel
from .indexing.order_indexes import Indexes

class Product(BaseDBModel):
    """
    Represents an order model
    """

    def __init__(self) -> None:
        super().__init__()        
        
        self.name: Optional[str] = None
        self.sku: Optional[str] = None
        self.type: Optional[str] = None
        self.triggers: Optional[list[str]] = None
        self.meta: Optional[dict] = {}
        self.price: Optional[float] = None
        self.sale_price: Optional[float] = None
        self.cost: Optional[float] = None
        self.category: Optional[str] = None
        self.keywords: Optional[list[str]] = None
        self.description: Optional[str] = None
        self.quantity_in_stock: Optional[int] = 0
        self.quantity_available: Optional[int] = 0
        self.quantity_reserved: Optional[int] = 0
        self.quantity_sold: Optional[int] = 0        
        self.quantity_returned: Optional[int] = 0
        self.quantity_shipped: Optional[int] = 0
        self.quantity_on_order: Optional[int] = 0
        self.quantity_on_back_order: Optional[int] = 0

        
        Indexes(self)

    



