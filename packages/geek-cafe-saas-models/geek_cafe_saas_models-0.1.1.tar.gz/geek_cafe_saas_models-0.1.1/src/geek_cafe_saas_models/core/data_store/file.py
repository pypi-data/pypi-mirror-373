from enum import Enum
from typing import Optional, Dict
from ..._base_tenant_user_model import BaseTenantUserDBModel as BaseDBModel
from .indexing.file_indexes import Indexes

class StorageType(str, Enum):
    DATABASE = "database"   # stored in a database
    FILE = "file"           # stored in a file system (available locally)
    CLOUD = "cloud"         # stored in a cloud service (S3, Azure, GCP, etx)    
    NAS = "nas"             # a network attached storage device (NFS, SMB, etx)
    FTP = "ftp"             # available via FTP
    API = "api"             # available via API    
    OTHER = "other"         # available via Other (all access/configuration is in metadata)

class FileStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    VALIDATING = "validating"
    READY = "ready"
    DELETED = "deleted"
    ERROR = "error"
    ARCHIVED = "archived"
    COLD_STORAGE = "cold_storage"
    

class File(BaseDBModel):
    """
    Represents a file, image, or binary data reference.
    Supports multiple storage backends (e.g., local, S3, DB).

    S3 File
    {
        "description": "Company Logo",
        "file_name": "logo.png",
        "content_type": "image/png",
        "storage_type": "cloud",
        "uri": "s3://my-bucket/assets/logo.png",
        "size_bytes": 34567,
        "status": "available",
        "metadata": {
            "provider": "aws",
            "bucket": "my-bucket",
            "key": "assets/logo.png"
        }
    }

    Local File
    {
        "description": "Company Logo",
        "file_name": "logo.png",
        "content_type": "image/png",
        "storage_type": "local",
        "uri": "file://Users/username/Documents/assets/logo.png",
        "size_bytes": 34567,
        "status": "available",
        "metadata": {
            "machine-name": "my-mac-book",
            "path": "/Users/username/Documents/assets/logo.png"
        }
    }

    Database:
    {
        "description": "License File",
        "file_name": "license.key",
        "content_type": "text/plain",
        "storage_type": "database",
        "uri": "blob#abc123",
        "status": "available",
        "metadata": {
            "table": "data_blobs",
            "record_id": "abc123"
        }
    }


    """
    def __init__(self):
        super().__init__()

        
        self.file_name: Optional[str] = None
        self.description: Optional[str] = None
        self.extension: Optional[str] = None
        self.content_type: Optional[str] = None  # MIME type

        self.storage_type: Optional[StorageType] = None
        self.uri: Optional[str] = None  # S3 URL, local path, DB key, etc.

        self.status: Optional[FileStatus] = FileStatus.PENDING
        self.size_bytes: Optional[int] = None
        self.checksum: Optional[str] = None  # Optional: SHA256 or MD5
        self.is_archived: Optional[bool] = False        
        self.category: Optional[str] = None
        
       
        Indexes(self)
