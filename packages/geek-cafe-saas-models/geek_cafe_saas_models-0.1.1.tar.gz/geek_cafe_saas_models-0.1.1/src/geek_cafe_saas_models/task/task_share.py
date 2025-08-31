from ..core.security.entity_access import EntityAccess
from . import Task
class TaskShare(EntityAccess):
    """
    Defines the sharing rights of an task
    
    """
    def __init__(self):
        super().__init__()

    
    @property
    def xref_type(self)-> str:
        """Fixed to a task model type"""
        return Task().model_name
    
    @xref_type.setter
    def xref_type(self, value: str):
        """Don't override the value, but leave the setter in place"""
        pass


