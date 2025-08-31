"""
Geek Cafe, LLC
MIT License.  See Project Root for the license information.
"""
from typing import Optional

from ..core.activity import Activity
class AssetActivity(Activity):
    def __init__(self):
        super().__init__()

        self.cost: Optional[float] = None # cost (if any) for this event
        self.xref_type = "asset"
        
    def __repr__(self):
        return f"Asset(name={self.name})"