
from typing import Optional
from .file import File

class Image(File):
    """
    An image file.    
    """

    def __init__(self):
        super().__init__()
        
        self.width: Optional[str] = None
        self.height : Optional[str] = None
        self.thumbnail : Optional[File] = None