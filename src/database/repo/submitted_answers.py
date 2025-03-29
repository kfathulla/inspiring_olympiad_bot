from sqlalchemy import select

from src.database.models.submitted_answers import SubmittedAnswer
from src.database.repo.base import BaseRepo


class SubmittedAnswerRepo(BaseRepo):
    async def get_submitted_answers_by_submission(self, submission_id: int):
        stmt = select(SubmittedAnswer).where(SubmittedAnswer.submission_id == submission_id)
        result = await self.session.execute(stmt)
        
        return result.scalars().all()
