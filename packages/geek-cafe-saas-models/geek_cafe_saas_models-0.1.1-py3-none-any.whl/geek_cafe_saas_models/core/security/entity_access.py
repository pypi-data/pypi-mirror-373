"""
Geek Cafe, LLC
MIT License.  See Project Root for the license information.
"""

from typing import Optional
from datetime import datetime
from ..._base_tenant_user_model import BaseTenantUserDBModel as BaseDBModel
from .indexing.entity_access_indexes import Indexes

class EntityAccess(BaseDBModel):
    def __init__(self):
        super().__init__()
        
        self.__access_levels: Optional[str] = []  # *, read, write, delete, etc.
        self.role: Optional[str] = None  # "family", "realtor", "contractor", "inspector"
        self.expires_at: Optional[datetime] = None
        self.shared_by_user_id: Optional[str] = None
        self.notes: Optional[str] = None  # Additional context for the access grant
        
        Indexes(self)

    @property
    def xref_type(self) -> str:
        """
        Setting access to a blanket type of resource
        """
        return self._xref_type or "*"

    @xref_type.setter
    def xref_type(self, value: str):
        """
        Setting access to a blanket type of resource
        """
        self._xref_type = value

    @property
    def xref_pk(self)->str:
        """
        Setting access to a specific resource
        """
        return self._xref_pk or "*"

    @xref_pk.setter
    def xref_pk(self, value: str):
        """
        Setting access to a specific resource
        """
        self._xref_pk = value

    @property
    def access_levels(self):
        if not isinstance(self.__access_levels, list):
            self.__access_levels = self.__access_levels.split(",")
        return self.__access_levels

    @access_levels.setter
    def access_levels(self, value: Optional[str] | list[str] = None):
        """
        "read", "write",  "list", "none",
        """
        if value is None:
            raise ValueError("Action cannot be None")

        if isinstance(value, str):
            value = value.split(",")

        self.__access_levels = value
