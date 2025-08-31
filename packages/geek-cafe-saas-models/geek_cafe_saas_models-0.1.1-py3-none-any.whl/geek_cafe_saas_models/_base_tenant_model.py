"""
Geek Cafe, LLC
MIT License.  See Project Root for the license information.
"""


from typing import Optional
from ._base_model import BaseDBModel


class BaseTenantDBModel(BaseDBModel):
    """
    The Base DB Model for Tenants
    Sets a common set of properties for all models
    """

    def __init__(self) -> None:
        super().__init__()
       
        self.tenant_id: Optional[str] = None        
       
     