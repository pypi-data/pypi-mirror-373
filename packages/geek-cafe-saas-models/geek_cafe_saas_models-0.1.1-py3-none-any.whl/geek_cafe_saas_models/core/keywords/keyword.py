"""
Geek Cafe, LLC
MIT License.  See Project Root for the license information.
"""

from typing import Optional

from ..._base_tenant_user_model import BaseTenantUserDBModel as BaseDBModel
from .indexing.keyword_indexes import Indexes


class Keyword(BaseDBModel):
    """
    Represents a keyword indexing model.  You can use this across all of your object
    to create a simple keyword search.  In your queries you can limit it to a specific type of model
    or open it up to all models.  A keyword name will link to the model
    """

    def __init__(self) -> None:
        super().__init__()

        self.name: Optional[str] = None
        self.match_pk: Optional[str] = None
        self.match_model_name: Optional[str] = None
        
        """
        The table name, useful if not using a single table design
        or if you keywords are not tied to a specific table
        """

        Indexes(self)
