from typing import Optional

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy import text, BIGINT, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship


from .base import Base, TimestampMixin, TableNameMixin


class TestAnswer(Base, TimestampMixin, TableNameMixin):
    __tablename__ = "test_answers"
    
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    order: Mapped[int] = mapped_column(Integer, default=0)
    text: Mapped[Optional[str]] = mapped_column(String(128))
    type: Mapped[int] = mapped_column(Integer, default=0) # 0 - yopiq test javobi, 1 - ochiq test javobi
    score: Mapped[float] = mapped_column(Numeric(precision=3, scale=2), default=0)

    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id"), nullable=False)
    test = relationship('Test', back_populates='answers')

    submitted_answers = relationship('SubmittedAnswer', back_populates='test_answer', lazy="noload")

    def __repr__(self):
        return f"<Test {self.id} {self.text}>"