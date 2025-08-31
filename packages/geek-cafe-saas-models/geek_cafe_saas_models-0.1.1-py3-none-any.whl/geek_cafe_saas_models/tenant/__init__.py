from typing import Optional
from .._base_model import BaseDBModel
from .indexing.tenant_indexes import Indexes
from .subscription import Subscription
class Tenant(BaseDBModel):
    """
    Represents a tenant model
    """

    def __init__(self) -> None:
        super().__init__()        
        
        self.name: Optional[str] = None
        self.description: Optional[str] = None
        self.contact_email: Optional[str] = None
        self.contact_phone: Optional[str] = None
        self.contact_first_name: Optional[str] = None
        self.contact_last_name: Optional[str] = None
        self.subscription: Optional[Subscription] = None
        self.status: Optional[str] = None
        self.type: Optional[str] = None  # e.g. user, family, organization, etc
        Indexes(self)

    



