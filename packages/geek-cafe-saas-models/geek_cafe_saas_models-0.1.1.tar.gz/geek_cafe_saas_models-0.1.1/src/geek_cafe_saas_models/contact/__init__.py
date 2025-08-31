"""
Geek Cafe, LLC
MIT License.  See Project Root for the license information.
"""

from typing import Optional

class Contact:
    def __init__(self):
        self.first_name: Optional[str] = None
        self.last_name: Optional[str] = None
        self.email: Optional[str] = None
        self.phone: Optional[str] = None