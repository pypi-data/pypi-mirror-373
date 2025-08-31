from typing import Optional
"""
Geek Cafe, LLC
MIT License.  See Project Root for the license information.
"""

from .._base_tenant_user_model import BaseTenantUserDBModel as BaseDBModel

class Booking:
    """
    User's booking for an in-person or live session.
    You can use a booking as a Ticket.  This is simply the model, on a front end you can call
    it whatever you want for clarity    
    """
    def __init__(self):
        
        self.event_id: Optional[str] = None
        self.status: Optional[str] = None
        self.created: Optional[str] = None
        self.updated: Optional[str] = None
        self.price: Optional[float] = None
        self.location: Optional[str] = None
        self.start_date: Optional[str] = None
        self.end_date: Optional[str] = None
        self.duration: Optional[float] = None
        

class Ticket(Booking):
    """Same as booking"""
    pass