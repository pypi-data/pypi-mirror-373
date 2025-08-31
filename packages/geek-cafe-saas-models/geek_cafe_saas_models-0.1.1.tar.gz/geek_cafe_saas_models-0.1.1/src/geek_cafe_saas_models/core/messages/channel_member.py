

from datetime import datetime, UTC
from typing import Optional
from ..._base_tenant_user_model import BaseTenantUserDBModel as BaseDBModel
# from .indexing.channel_indexes import Indexes


class MessageChannelMember(BaseDBModel):
    """
    A message "channel" member, and their roles
    """
    def __init__(self):
        super().__init__()
        self.channel_id: Optional[str] = None
        self.member_id: Optional[str] = None
        self.joined_utc_ts: Optional[float] = datetime.now(tz=UTC).timestamp()
        self.roles: Optional[list[str]] = None