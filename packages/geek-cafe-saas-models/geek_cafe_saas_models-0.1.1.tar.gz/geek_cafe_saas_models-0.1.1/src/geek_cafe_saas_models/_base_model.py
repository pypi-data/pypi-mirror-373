"""
Geek Cafe, LLC
MIT License.  See Project Root for the license information.
"""

import datetime as dt
from boto3_assist.utilities.string_utility import StringUtility
from boto3_assist.dynamodb.dynamodb_model_base import (
    DynamoDBModelBase,
    exclude_from_serialization,
)
from boto3_assist.utilities.string_utility import StringUtility
from typing import Optional, Dict, Any


class BaseDBModel(DynamoDBModelBase):
    """
    The Base DB Model
    Sets a common set of properties for all models
    """

    def __init__(self) -> None:
        super().__init__()
        self.id: str = StringUtility.generate_sortable_uuid()  # make the id's sortable
        self.__created_utc: dt.datetime = dt.datetime.now(dt.UTC)
        self.__updated_utc: dt.datetime = dt.datetime.now(dt.UTC)
        self.__deleted_utc: Optional[dt.datetime] = None

        self.__model_version: str = "1.0.0"
        self._metadata: Dict[str, Any] | None = None
        self._xref_pk: Optional[str] = (
            None  # Optional primary key of the item it's related to used for relationships
        )
        self._xref_type: Optional[str] = None
        self._xref_pk_required: bool = False
        self._xref_type_required: bool = False
        self._table_name: Optional[str] = None
        self.create_by_id: Optional[str]= None
        self.updated_by_id: Optional[str]= None
        self.deleted_by_id: Optional[str]= None
        self.version: float= 1.0
    
    @property
    def created_utc(self) -> dt.datetime:
        """
        Returns the created date for this model
        """
        return self.__created_utc

    @created_utc.setter
    def created_utc(self, value: dt.datetime | str):
        """
        Defines the created date for this model
        """
        if value is None:
            self.__created_utc = dt.datetime.now(dt.UTC)
            return
        if isinstance(value, str):
            value = dt.datetime.fromisoformat(value)
        self.__created_utc = value


    
    def created_utc_ts(self) -> float:
        return self.updated_utc.timestamp()

    


    @property
    def updated_utc(self) -> dt.datetime:
        """
        Returns the updated date for this model
        """
        return self.__updated_utc

    @updated_utc.setter
    def updated_utc(self, value: dt.datetime | str):
        """
        Defines the updated date for this model
        """
        if value is None:
            self.__updated_utc = dt.datetime.now(dt.UTC)
            return
        if isinstance(value, str):
            value = dt.datetime.fromisoformat(value)
        self.__updated_utc = value

    
    def updated_utc_ts(self) -> float:
        return self.updated_utc.timestamp()

   

    @property
    def deleted_utc(self) -> dt.datetime:
        """
        Returns the deleted date for this model
        """
        return self.__deleted_utc

    @deleted_utc.setter
    def deleted_utc(self, value: dt.datetime | str):
        """
        Defines the deleted date for this model
        """
        if value is None:
            self.__deleted_utc = dt.datetime.now(dt.UTC)
            return
        if isinstance(value, str):
            value = dt.datetime.fromisoformat(value)
        self.__deleted_utc = value

    
    def is_deleted(self) -> bool:
        """
        Returns True if the model is deleted
        """
        if self.__deleted_utc and isinstance(self.__deleted_utc, dt.datetime):            
            return self.__deleted_utc < dt.datetime.now(dt.UTC)
        return False
    
    

    @property
    def model_version(self) -> str:
        """
        Returns the model version for this model
        """
        return self.__model_version

    @model_version.setter
    def model_version(self, value: str):
        """
        Defines a model version.  All will start with the base model
        version, but you can override this as your model changes.
        Use your services to parse the older models correct (if needed)
        Which means a custom mapping of data between versioning for
        backward compatibility
        """
        self.__model_version = value

    @property
    def model_name(self) -> str:
        """
        Returns the record type for this model
        """
        return StringUtility.camel_to_snake(self.__class__.__name__)

    @model_name.setter
    def model_name(self, value: str):
        """
        This is read-only but we don't want an error during serialization
        """
        pass

    @property
    def model_name_plural(self) -> str:
        """
        Returns the record type for this model
        """
        return self.model_name + "s"

    @model_name_plural.setter
    def model_name_plural(self, value: str):
        """
        This is read-only but we don't want an error during serialization
        """
        pass

    @property
    def xref_pk(self):
        """
        Cross reference primary key.  Used for relationship building.
        To enforce set self._xref_pk_required
        """
        if self._xref_pk is None and self._xref_pk_required:
            if not self.serialization_in_progress():
                raise ValueError("xref_pk is not set")
        return self._xref_pk

    @xref_pk.setter
    def xref_pk(self, value: str | None):
        self._xref_pk = value

    @property
    def xref_type(self):
        """
        The Xref (cross reference / child) model name (model_name)
        """
        if self._xref_type is None and self._xref_type_required:
            if not self.serialization_in_progress():
                raise ValueError("xref_type is not set")

        return self._xref_type

    @xref_type.setter
    def xref_type(self, value: str | None):
        self._xref_type = value

    @property
    def table_name(self) -> str | None:
        """
        Returns the table name for this model.
        This is useful if you create multiple tables
        For a single table design you can leave this as null
        """
        return self._table_name

    @table_name.setter
    def table_name(self, value: str | None):
        """
        Defines the table name for this model
        """
        self._table_name = value

    
    @property
    def metadata(self) -> Dict[str, Any] | None:
        """
        Returns the metadata for this model
        """
        return self._metadata
    
    @metadata.setter
    def metadata(self, value: Dict[str, Any] | None):
        """
        Defines the metadata for this model
        """

        if not isinstance(value, dict):
            raise ValueError("metadata must be a dictionary")

        self._metadata = value

    def get_pk_id(self) -> str:
        """
        Returns the fully formed primary key for this model.
        This is typically in the form of "<resource_type>#<guid>"
        """
        pk = self.to_resource_dictionary().get("pk", None)
        if not pk:
            raise ValueError("The primary key is not set")
        return pk

    def to_float_or_none(self, value: Any) -> float | None:
        """
        Converts a value to a float or None
        """
        if isinstance(value, str):
            value = value.strip().replace("$", "").replace(",", "").replace(".", "")

        if value is None:
            return None
        try:
            return float(value)
        except:
            return None
