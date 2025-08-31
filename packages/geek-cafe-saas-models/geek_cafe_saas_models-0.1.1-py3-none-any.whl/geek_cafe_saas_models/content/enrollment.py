from typing import Optional
import datetime as dt

from .._base_model import BaseDBModel
from .enrollment_indexes import Indexes

class Enrollment(BaseDBModel):
    """
    Represents an enrollment model for access to private content
    """

    def __init__(self) -> None:
        super().__init__()        
        self.user_id: Optional[str] = None
        self.content_id: Optional[str] = None
        self.start_date_utc: Optional[dt.datetime] = None
        self.expiration_date_utc: Optional[dt.datetime] = None
            
        Indexes(self)

