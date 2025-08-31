"""
Geek Cafe, LLC
MIT License.  See Project Root for the license information.
"""
from typing import Optional

from ..core.activity import Activity
class TaskActivity(Activity):
    """
    Creates an activity entry for a task event
    
    """
    def __init__(self):
        super().__init__()
        
        self.xref_type = "task"
        
    def __repr__(self):
        return f"Asset(name={self.name})"