"""
Geek Cafe, LLC
MIT License.  See Project Root for the license information.
"""
import datetime as dt
from typing import Optional
from datetime import datetime
from ..._base_tenant_user_model import BaseTenantUserDBModel as BaseDBModel
from .indexing.relationship_indexes import Indexes

class Relationship(BaseDBModel):

    def __init__(self):
        super().__init__()
        
        self.__start_utc: Optional[datetime] = None
        self.__end_utc: Optional[datetime] = None
        
        self._xref_pk_required = True
        self._xref_type_required = True

        Indexes(self)

    def get_start_date_utc_ts(self):
        if self.__start_utc is None:
            return None
        else:
            return self.__start_utc.timestamp()
        
    def get_end_date_utc_ts(self):
        if self.__end_utc is None:
            return None
        else:
            return self.__end_utc.timestamp()
            

    @property
    def type(self)->str:
        """Examples: assigned_to, owned_by"""
        if not self.serialization_in_progress():
            if self._type is None:
                raise ValueError("type is not set")
        return self._type
    
    @type.setter
    def type(self, value: str):        
        self._type = value

    @property
    def start_utc(self) -> dt.datetime:
        """
        Returns the created date for this model
        """
        return self.__start_utc
    
    @start_utc.setter
    def start_utc(self, value: dt.datetime | str):
        """
        Defines the created date for this model
        """
        if value is None:
            self.__start_utc = dt.datetime.now(dt.UTC)
            return
        if isinstance(value, str):
            value = dt.datetime.fromisoformat(value)
        self.__start_utc = value

    @property
    def end_utc(self) -> dt.datetime:
        """
        Returns the updated date for this model
        """
        return self.__end_utc
    
    @end_utc.setter
    def end_utc(self, value: dt.datetime | str):
        """
        Defines the updated date for this model
        """
        if value is None:
            self.__end_utc = dt.datetime.now(dt.UTC)
            return
        if isinstance(value, str):
            value = dt.datetime.fromisoformat(value)
        self.__end_utc = value
    
