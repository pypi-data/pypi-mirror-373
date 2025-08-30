from datetime import datetime
from typing import Optional

from pydantic import BaseModel, model_validator, validator


class DateRange(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    @validator('start_date', 'end_date')
    def validate_date(cls, value):
        assert value is None or value.tzinfo, 'date is missing time zone'
        return value

    @model_validator(mode="before")
    @classmethod
    def validate_start_date_and_end_date(cls, values):
        start_date = values.get('start_date')
        end_date = values.get('end_date')
        if start_date and end_date:
            assert start_date <= end_date, 'date_range start date is after end_date'
        return values

    @property
    def start_epoch_time(self):
        epoch_time = self.start_date.timestamp() if self.start_date else 0
        return epoch_time

    @property
    def end_epoch_time(self):
        epoch_time = self.end_date.timestamp() if self.end_date else float('inf')
        return epoch_time


class BoundedDateRange(DateRange):
    @model_validator(mode="before")
    @classmethod
    def validate_start_date_and_end_date(cls, values):
        start_date = values.get('start_date')
        end_date = values.get('end_date')
        assert start_date, 'bounded date_range missing start_date'
        assert end_date, 'bounded date_range missing end_date'
        # https://github.com/pydantic/pydantic/pull/2670 pydantic bug fixed in 2.6 but we are not in that version
        # since pydantic 2.6, parent root validator will not be called if overriden
        assert start_date <= end_date, 'date_range start_date is after end_date'
        return values
