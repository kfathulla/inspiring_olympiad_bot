from datetime import datetime

from src.models.base import BaseFilter


class UserFilter(BaseFilter):
    updated_datetime_to: datetime | None
    updated_datetime_from: datetime | None

    def __init__(self, updated_datetime_from: datetime | None, updated_datetime_to: datetime | None):
        self.updated_datetime_from = updated_datetime_from
        self.updated_datetime_to = updated_datetime_to
        BaseFilter.__init__(self)
