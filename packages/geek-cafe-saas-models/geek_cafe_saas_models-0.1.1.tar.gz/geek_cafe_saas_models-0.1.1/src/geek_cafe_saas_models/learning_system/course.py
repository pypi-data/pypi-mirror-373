"""
Geek Cafe, LLC
MIT License.  See Project Root for the license information.
"""

from typing import Optional

from .._base_model import BaseDBModel

class Course(BaseDBModel):
    """
    A Course or Class definition.  This simply defines the course.
    To Schedule a course you can create one or more events.
    """
    def __init__(self):
        self.name: Optional[str] = None
        self.description: Optional[str] = None
        self.duration: Optional[float] = None
        self.duration_unit: Optional[str] = None
        self.price: Optional[float] = None
        """NOTE: this is a starting/template price.  You can change this for each scheduled event."""