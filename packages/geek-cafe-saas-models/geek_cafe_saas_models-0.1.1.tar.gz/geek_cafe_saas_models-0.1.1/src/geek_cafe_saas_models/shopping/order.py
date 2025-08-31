from typing import Optional
import datetime as dt

from .._base_tenant_user_model import BaseTenantUserDBModel as BaseDBModel
from .indexing.order_indexes import Indexes

class Order(BaseDBModel):
    """
    Represents an order model
    """

    def __init__(self) -> None:
        super().__init__()        
        
        
        self.order_date: Optional[dt.datetime] = None
        self.order_status: Optional[str] = None
        self.order_total: Optional[float] = None
        self.order_subtotal: Optional[float] = None
        self.order_tax: Optional[float] = None
        self.order_discount: Optional[float] = None
        self.order_shipping: Optional[float] = None
        self.order_shipping_address: Optional[str] = None
        self.order_billing_address: Optional[str] = None
        self.completed_date_utc: Optional[dt.datetime] = None
        Indexes(self)

    



