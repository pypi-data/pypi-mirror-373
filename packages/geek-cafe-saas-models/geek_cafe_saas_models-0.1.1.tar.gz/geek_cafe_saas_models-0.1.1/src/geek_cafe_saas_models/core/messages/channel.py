


from typing import Optional
from ..._base_tenant_user_model import BaseTenantUserDBModel as BaseDBModel
# from .indexing.channel_indexes import Indexes


class MessageChannel(BaseDBModel):
    """
    A message "channel"
    """
    def __init__(self):
        super().__init__()
        self.name: Optional[str] = None
        self.owner_id: Optional[str] = None
        self.description: Optional[str] = None
        self.channel_type: str = "discussion"  # "discussion", "property", "project"
        self.is_private: bool = False
        