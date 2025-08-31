"""
Geek Cafe, LLC
MIT License.  See Project Root for the license information.
"""

from typing import Optional
from .._base_tenant_user_model import BaseTenantUserDBModel as BaseDBModel
from .indexing.task_indexes import Indexes
import datetime as dt


class Task(BaseDBModel):
    def __init__(self):
        super().__init__()
        self._subject: Optional[str] = None
        self._category: Optional[str] = None  # category or type of the task
        self._status: Optional[str] = None  # status of the task]
        self._percent_completed: float = 0.0        
        self._start_target_utc: Optional[dt.datetime] = None
        self._start_actual_utc: Optional[dt.datetime] = None
        self._due_date_utc: Optional[dt.datetime] = None
        self._completed_actual_utc: Optional[dt.datetime] = None
        self._estimated_cost: Optional[float] = None
        self._actual_cost: Optional[float] = None
        self._detail: Optional[str] = None
        Indexes(self)


    @property
    def subject(self):
        return self._subject
    
    @subject.setter
    def subject(self, value: str):
        self._subject = value

    @property
    def detail(self):
        return self._detail
    @detail.setter
    def detail(self, value: str):
        self._detail = value

    @property
    def estimated_cost(self):
        return self._estimated_cost
    
    @estimated_cost.setter
    def estimated_cost(self, value: float):
        if value is None:
            value = 0.0  #
        if not isinstance(value, float):
            t = type(value)
            raise ValueError(f"Estimated Cost must be a float. Got {t} instead")
        
        self._estimated_cost = value

    @property
    def actual_cost(self):
        return self._actual_cost
    
    @actual_cost.setter
    def actual_cost(self, value: float):
        if value is None:
            value = 0.0  #
        if not isinstance(value, float):
            t = type(value)
            raise ValueError(f"Actual Cost must be a float. Got {t} instead")
        self._actual_cost = value

    

    @property
    def category(self):
        return self._category
    
    @category.setter
    def category(self, value: str):
        self._category = value

    @property
    def status(self):
        if not self._status:
            self._status = "Not Started"
        return self._status

    @status.setter
    def status(self, value: str):
        self._status = value

    @property
    def percent_completed(self):
        return self._percent_completed

    @percent_completed.setter
    def percent_completed(self, value: float):
        if not value or value < 0:
            self._percent_completed = 0.0

    
    @property
    def start_target_utc(self):
        return self._start_target_utc
    
    @start_target_utc.setter
    def start_target_utc(self, value: dt.datetime | str | None):

        if isinstance(value, str):
            value = dt.datetime.fromisoformat(value)
        self._start_target_utc = value

    @property
    def start_actual_utc(self):
        return self._start_actual_utc
    
    @start_actual_utc.setter
    def start_actual_utc(self, value: dt.datetime| str | None):
        if isinstance(value, str):
            value = dt.datetime.fromisoformat(value)
        self._start_actual_utc = value

    @property
    def due_date_utc(self):
        return self._due_date_utc
    
    @due_date_utc.setter
    def due_date_utc(self, value: dt.datetime| str | None):
        if isinstance(value, str):
            value = dt.datetime.fromisoformat(value)
        self._due_date_utc = value

    @property
    def completed_actual_utc(self):
        return self._completed_actual_utc
    
    @completed_actual_utc.setter
    def completed_actual_utc(self, value: dt.datetime| str | None):
        if isinstance(value, str):
            value = dt.datetime.fromisoformat(value)
        self._completed_actual_utc = value


    def __repr__(self):
        return f"Asset(subject={self.subject})"
