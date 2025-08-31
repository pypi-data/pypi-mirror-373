"""
Geek Cafe, LLC
MIT License.  See Project Root for the license information.
"""


from typing import Optional, Dict, Any
from .._base_tenant_user_model import BaseTenantUserDBModel as BaseDBModel
from .indexing.asset_indexes import Indexes

class Asset(BaseDBModel):
    def __init__(self):
        super().__init__()
        self.name: Optional[str] = None                
        self.category: Optional[str] = None     # category or type of the asset
                     

        Indexes(self)

    def __repr__(self):
        return f"Asset(name={self.name})"