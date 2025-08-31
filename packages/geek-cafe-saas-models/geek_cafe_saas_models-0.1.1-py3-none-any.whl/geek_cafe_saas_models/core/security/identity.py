"""
Geek Cafe, LLC
MIT License.  See Project Root for the license information.
"""

from typing import Optional

from ..._base_tenant_user_model import BaseTenantUserDBModel as BaseDBModel
from .indexing.identity_indexes import Indexes
class Identity(BaseDBModel):
    """
    Represents an Identity model.  This allows a user to link up with a specific Identity
    Provider or allow federation from Cognito to Office365,
    """

    def __init__(self) -> None:
        super().__init__()        
        
        
        self.provider: Optional[str] = None
        self.provider_user_id: Optional[str] = None
        self.status: Optional[str] = None

        Indexes(self)

    



