from ..core.security.entity_access import EntityAccess
from .asset import Asset
class AssetSecurity(EntityAccess):
    def __init__(self):
        super().__init__()

    
    @property
    def xref_type(self)-> str:
        """We are specifically assigning access rights to an asset"""
        return Asset().model_name
    
    @xref_type.setter
    def xref_type(self, value: str):
        """Don't override the value, but leave the setter in place"""
        pass


