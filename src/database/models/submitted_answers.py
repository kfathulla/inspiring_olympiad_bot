from typing import Optional

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, false
from sqlalchemy import text, BIGINT, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models.tests import Test

from .base import Base, TimestampMixin, TableNameMixin


class SubmittedAnswer(Base, TimestampMixin, TableNameMixin):
    __tablename__ = "submitted_answers"
    
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    text: Mapped[Optional[str]] = mapped_column(String(128))
    
    is_correct: Mapped[bool] = mapped_column(Boolean, server_default=false())
    score: Mapped[float] = mapped_column(Numeric(precision=3, scale=2), default=0)

    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id"), nullable=False)
    submission = relationship('Submission', back_populates='submitted_answers')

    test_answer_id: Mapped[int] = mapped_column(ForeignKey("test_answers.id"), nullable=False)
    test_answer = relationship('TestAnswer', back_populates='submitted_answers', lazy="joined", innerjoin=True)

    def __repr__(self):
        return f"<Submission Answer {self.id} {self.text}>"