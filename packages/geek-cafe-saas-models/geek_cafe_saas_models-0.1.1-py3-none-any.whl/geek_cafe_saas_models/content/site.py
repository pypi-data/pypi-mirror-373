from typing import Optional
from .._base_model import BaseDBModel

class Site(BaseDBModel):
    """Site"""
    def __init__(self, name: Optional[str] = None):
        self.name:Optional[str] = name
        self.primary_dns: Optional[str] = None
        