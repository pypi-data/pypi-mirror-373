from typing import Optional
import datetime as dt

from .._base_tenant_user_model import BaseTenantUserDBModel as BaseDBModel
from .indexing.order_indexes import Indexes

class OrderItem(BaseDBModel):
    """
    Represents an order model
    """

    def __init__(self) -> None:
        super().__init__()        
        
        self.product_id: Optional[str] = None
        self.original_price: Optional[float] = None
        self.discount_price: Optional[float] = None
        self.quantity: Optional[int] = None
        self.subtotal: Optional[float] = None
        self.tax: Optional[float] = None
        self.total: Optional[float] = None
        self.order_id: Optional[str] = None
        
        
        
        
        Indexes(self)

    



