

from typing import Optional
from ..._base_tenant_user_model import BaseTenantUserDBModel as BaseDBModel
# from .indexing.message_indexes import Indexes


class MessageReaction(BaseDBModel):
    def __init__(self) -> None:
        super().__init__()

        self.message_id: Optional[str] = None
        self.recipient_id: Optional[str] = None
        self.reaction: Optional[str] = None
        self.reaction_type: Optional[str] = None # emoji, etc
        # Indexes(self)