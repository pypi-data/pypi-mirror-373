"""
Geek Cafe, LLC
MIT License.  See Project Root for the license information.
"""

import os
from typing import Optional
from datetime import datetime

from ..._base_tenant_user_model import BaseTenantUserDBModel as BaseDBModel
from .indexing.user_indexes import Indexes


class User(BaseDBModel):
    """
    Represents a user model
    """

    def __init__(self) -> None:
        super().__init__()

        self.idp_user_id: Optional[str] = None
        """User Name / Id stored in the IdP"""
        self.first_name: Optional[str] = None
        self.last_name: Optional[str] = None
        self.email: Optional[str] = None
        self.phone: Optional[str] = None
        self.description: Optional[str] = None
        self.scopes: Optional[list[str]] = None
        self.last_login_date_utc: Optional[datetime] = None
        self.__password_hashed: Optional[str] = None
        Indexes(self)

    @property
    def password_hashed(self) -> Optional[str]:
        """
        A password that is hashed.
        We strongly recommend using an IdP and staying away from using and storing a password.
        However we understand that it may not be possible so use a password with caution.
        NOTE:
            Using this field will emit warnings unless you set an environment
            variable of "SUPPRESS_PASSWORD_USAGE_WARNINGS"="true"
        """
        self.__emit_password_usage_warning()
        return self.__password_hashed

    @password_hashed.setter
    def password_hashed(self, value: str) -> None:
        self.__password_hashed = value
        self.__emit_password_usage_warning()

    def __emit_password_usage_warning(self):
        """
        Emit a warning that the password property is being used.
        You can disable this with an environment variable.  But as a best practice it is enabled by default
        """
        if str(os.getenv("SUPPRESS_PASSWORD_USAGE_WARNINGS", None)).lower() in [
            "true",
            "1",
            "t",
        ]:
            return

        import warnings

        warnings.warn(
            "You are using a password in the architecture and we strongly "
            "suggest switching to an IdP. To disable this message set an environment "
            "variable of SUPPRESS_PASSWORD_USAGE_WARNINGS=true",
            stacklevel=2,
        )
