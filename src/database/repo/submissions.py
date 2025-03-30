from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.database.models.submissions import Submission
from src.database.repo.base import BaseRepo


class SubmissionRepo(BaseRepo):
    async def add_submission(self, submission: Submission):
        self.session.add(submission)

        await self.session.commit()
        return await self.session.get(
            Submission, submission.id, options=[selectinload(Submission.submitted_answers)]
        )

    async def get_submission_by_id(self, id):
        stmt = select(Submission).where(Submission.id == id)
        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def get_submissions_by_test(self, test_id: int):
        stmt = select(Submission).where(Submission.test_id == test_id).order_by(Submission.score.desc(), Submission.correct_count.desc())
        result = await self.session.execute(stmt)

        return result.scalars().all()

    async def get_submissions_by_user(self, user_id: int):
        stmt = select(Submission).where(Submission.user_id == user_id)
        result = await self.session.execute(stmt)

        return result.scalars().all()

    async def get_user_submissions_by_test(self, user_id: int, test_id: int):
        stmt = select(Submission).where(
            (Submission.user_id == user_id) & (Submission.test_id == test_id)
        )
        result = await self.session.execute(stmt)

        return result.scalars().all()

    async def update_submission(self, submission: Submission, **kwargs):
        for key, value in kwargs.items():
            if hasattr(submission, key):
                setattr(submission, key, value)

        await self.session.commit()

        return submission
