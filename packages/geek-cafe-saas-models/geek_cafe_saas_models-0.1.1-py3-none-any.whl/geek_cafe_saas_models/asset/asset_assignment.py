from typing import Literal
from ..core.joins.relationship import Relationship
from . import Asset
class AssetAssignment(Relationship):
    """
    Defines a join record for the asset (owners vs assigned to).
    This does not define the security of what someone could do.
    We may want to revisit this??
    """
    def __init__(self):
        super().__init__()
        
    
    @property
    def type(self)-> Literal["assigned_to", "owned_by"]:
        """The asset id"""
        return self._type

    @type.setter
    def type(self, value: Literal["assigned_to", "owned_by"]):
        """The asset id"""
        self._type = value

    @property
    def xref_type(self)-> str:
        """We are specifically assigning access rights to an asset"""
        return Asset().model_name
    
    @xref_type.setter
    def xref_type(self, value: str):
        """Don't override the value, but leave the setter in place"""
        pass