
from typing import Optional
from .file import File

class Video(File):
    """
    A video file.    
    """

    def __init__(self):
        super().__init__()
        self.duration: Optional[str] = None
        self.width: Optional[str] = None
        self.height : Optional[str] = None
        self.thumbnail : Optional[str] = None