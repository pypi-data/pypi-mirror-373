
"""
Geek Cafe, LLC
MIT License.  See Project Root for the license information.
"""

from typing import Optional
from .._base_tenant_user_model import BaseTenantUserDBModel as BaseDBModel
from .indexing.asset_tag_indexes import Indexes

class AssetTag(BaseDBModel):
    """
    Keywords Associated to the Asset.  Create a unique entry for each Keyword
    Keywords are used for searching a specific 
    """
    def __init__(self):
        super().__init__()
        self.name: Optional[str] = None  # the name of the keyword        
        self.description : Optional[float] = None # additional information about the keyword
        self.asset_id: Optional[str] = None # the asset that this keyword is associated with
        

        Indexes(self)
