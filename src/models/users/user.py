import datetime


class User:
    id: int
    username: str
    first_name: str | None
    last_name: str | None
    phone_number: str | None
    telegram_id: int
    created_datetime: datetime.datetime | None
    updated_datetime: datetime.datetime | None
    is_deleted: bool

    def __init__(self):
        self.id = 0
        self.username = ""
        self.first_name = None
        self.last_name = None
        self.phone_number = None
        self.telegram_id = 0
        self.created_datetime = None
        self.updated_datetime = None
        self.is_deleted = False
