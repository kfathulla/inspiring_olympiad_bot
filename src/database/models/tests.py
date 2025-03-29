from datetime import datetime
from typing import List, Optional

from sqlalchemy import TIMESTAMP, ForeignKey, String, func
from sqlalchemy import BIGINT, Boolean, false
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, TableNameMixin


class Test(Base, TimestampMixin, TableNameMixin):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    user = relationship('User', back_populates='tests')
    name: Mapped[Optional[str]] = mapped_column(String(128))
    is_show_correct_count: Mapped[bool] = mapped_column(Boolean, server_default=false())
    is_show_incorrects: Mapped[bool] = mapped_column(Boolean, server_default=false())
    is_show_answers: Mapped[bool] = mapped_column(Boolean, server_default=false())
    is_finished: Mapped[bool] = mapped_column(Boolean, server_default=false())
    
    finished_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    test_answers = relationship('TestAnswer', back_populates='test', lazy="noload")
    submissions = relationship('Submission', back_populates='test', lazy="noload")

    def __repr__(self):
        return f"<Test {self.id} {self.name}>"