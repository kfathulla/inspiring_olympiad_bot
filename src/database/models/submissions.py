from typing import Optional

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy import text, BIGINT, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models.tests import Test

from .base import Base, TimestampMixin, TableNameMixin


class Submission(Base, TimestampMixin, TableNameMixin):    
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    text: Mapped[Optional[str]] = mapped_column(String(1024))
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    incorrect_count: Mapped[int] = mapped_column(Integer, default=0)
    score: Mapped[float] = mapped_column(Numeric(precision=3, scale=2), default=0)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    user = relationship('User', back_populates='submissions', lazy="joined", innerjoin=True)
    
    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id"), nullable=False)
    test = relationship('Test', back_populates='submissions', lazy="joined", innerjoin=True)

    submitted_answers = relationship('SubmittedAnswer', back_populates='submission', lazy="noload")

    def __repr__(self):
        return f"<Submission {self.id} {self.text}>"