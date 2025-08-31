from typing import Optional
from .._base_tenant_user_model import BaseTenantUserDBModel as BaseDBModel
from datetime import datetime, UTC

class Subscription(BaseDBModel):

    """A Subscription Model"""
    def __init__(self):
        
        self.plan: Optional[str] = None
        self.status: Optional[str] = None
        self.billing_cycle: Optional[str] = None
        self.start_date_utc: Optional[datetime] = None
        self.end_date_utc: Optional[datetime] = None
        self.last_payment_date_utc: Optional[datetime] = None
        self.payment_amount: Optional[float] = None
        self.payment_currency: Optional[str] = None
        self.payment_method: Optional[str] = None
        self.next_payment_date_utc: Optional[datetime] = None
        self.next_payment_amount: Optional[float] = None
        self.grace_period_days: Optional[int] = 5
        
    
    def is_expired(self)->bool:
        if self.end_date_utc is None:
            return False
        if self.end_date_utc.tzinfo is None:
                self.end_date_utc = self.end_date_utc.replace(tzinfo=UTC)

        expired= self.end_date_utc + self.grace_period_days < datetime.now(UTC)
        return expired

        