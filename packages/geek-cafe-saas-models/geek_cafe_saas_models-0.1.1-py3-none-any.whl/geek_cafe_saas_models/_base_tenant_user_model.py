"""
Geek Cafe, LLC
MIT License.  See Project Root for the license information.
"""


from typing import Optional
from ._base_tenant_model import BaseTenantDBModel


class BaseTenantUserDBModel(BaseTenantDBModel):
    """
    The Base DB Model for Tenant Users
    Sets a common set of properties for all models
    """

    def __init__(self) -> None:
        super().__init__()
       
        self.user_id: Optional[str] = None        
        self._owner_id: Optional[str] = None
    
    @property
    def owner_id(self) -> Optional[str]:
        """
        The owner of the record. In most cases it's
        the user by if this is a copy of a record for sharing
        then it is likely not.
        """
        return self._owner_id or self.user_id
    

    @owner_id.setter
    def owner_id(self, value: Optional[str]):
        """
        The owner of the record
        """
        self._owner_id = value
        


    def is_owner(self, user_id: str) -> bool:
        """
        Is the user the owner of the record
        """
        return user_id == self.owner_id
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(user_id={self.user_id}, owner_id={self.owner_id})"