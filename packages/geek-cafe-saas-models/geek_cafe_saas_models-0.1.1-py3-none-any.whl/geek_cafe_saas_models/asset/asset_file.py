
from ..core.data_store.file import File
from . import Asset
class AssetFile(File):
    """
    A file tied to an asset or asset life cycle.
    Use xref_pk and xref_type  
    """
    def __init__(self):
        super().__init__()
        
        self._xref_type = Asset().model_name

    