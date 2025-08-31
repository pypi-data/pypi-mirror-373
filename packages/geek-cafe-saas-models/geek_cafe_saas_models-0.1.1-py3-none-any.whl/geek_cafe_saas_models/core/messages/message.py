

from typing import Optional
from datetime import datetime
from ..._base_tenant_user_model import BaseTenantUserDBModel as BaseDBModel
from .indexing.message_indexes import Indexes


class Message(BaseDBModel):
    def __init__(self) -> None:
        super().__init__()

        self.content: Optional[str] = None
        self.sender_id: Optional[str] = None
        self.channel_id: Optional[str] = None
        self.thread_id: Optional[str] = None  # For replies/threading
        self.message_type: str = "text"  # "text", "file", "system", "notification"
        self.reply_to_message_id: Optional[str] = None
        self.edited_at: Optional[datetime] = None
        self.is_deleted: bool = False

        Indexes(self)