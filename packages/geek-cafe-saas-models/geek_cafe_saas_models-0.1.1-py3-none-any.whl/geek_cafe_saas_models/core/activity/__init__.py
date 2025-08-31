
"""
Geek Cafe, LLC
MIT License.  See Project Root for the license information.
"""

from datetime import datetime
from typing import Optional
from ..._base_tenant_user_model import BaseTenantUserDBModel as BaseDBModel
from .indexing.activity_indexes import Indexes
class Activity(BaseDBModel):
    def __init__(self):
        super().__init__()
        self.name: Optional[str] = None             
        self.description : Optional[str] = None
        self.category: Optional[str] = None # purchase, sale, transfer, maintenance, etc.
        self.date_utc: Optional[datetime] = None                
        self.duration: Optional[float] = None # duration of the event
        self._cost: Optional[float] = None
        self._xref_pk_required = True # we're requiring a a pk reference to another item
        self._xref_type_required = True

        Indexes(self)

    @property
    def cost(self):
        return self._cost
    
    @cost.setter
    def cost(self, value):
        self._cost = self.to_float_or_none(value)

    def get_date_utc_ts(self):
        return self.to_timestamp_or_none(self.date_utc)
        

    def __repr__(self):
        return f"Asset(name={self.name})"