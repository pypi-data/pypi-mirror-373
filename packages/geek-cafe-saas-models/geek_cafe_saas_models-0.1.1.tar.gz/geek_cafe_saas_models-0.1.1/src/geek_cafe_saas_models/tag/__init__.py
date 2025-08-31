"""
Geek Cafe, LLC
MIT License.  See Project Root for the license information.
"""


from typing import Optional, Dict, Any
from .._base_tenant_user_model import BaseTenantUserDBModel as BaseDBModel
from .indexing.tag_indexes import Indexes

class Tag(BaseDBModel):
    def __init__(self):
        super().__init__()
        self.name: Optional[str] = None                
        self.description: Optional[str] = None
                     

        Indexes(self)

    def __repr__(self):
        return f"Asset(name={self.name})"