from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload

from src.database.models.tests import Test
from src.database.models.submissions import Submission
from src.database.repo.base import BaseRepo


class TestRepo(BaseRepo):
    async def insert_test(self, test: Test):
        self.session.add(test)

        await self.session.commit()
        return await self.session.get(
            Test, test.id, options=[selectinload(Test.answers)]
        )

    async def get_all_tests(self, user_id):
        stmt = (
            select(
                Test,
                # total submissions (all users)
                func.count(Submission.id).label("submissions_count"),
                # user submission for this test
                (
                    select(Submission.id)
                    .filter(
                        Submission.test_id == Test.id, Submission.user_id == user_id
                    )
                    .limit(1)
                )
                .correlate(Test)
                .scalar_subquery()
                .label("user_submission_id"),
            )
            .outerjoin(Test.submissions)
            .where(
                or_(
                    Test.is_public,
                    Test.user_id == user_id,
                    Test.submissions.any(Submission.user_id == user_id),
                )
            )
            .options(selectinload(Test.submissions))
            .group_by(Test.id)
        )

        result = await self.session.execute(stmt)
        return result.all()

    async def get_test_by_id(self, id):
        stmt = select(Test).options(selectinload(Test.answers)).where(Test.id == id)
        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def get_tests_by_user(self, user_id: int):
        stmt = select(Test).where(Test.user_id == user_id)
        result = await self.session.execute(stmt)

        return result.scalars().all()

    async def update_test(self, test: Test, **kwargs):
        for key, value in kwargs.items():
            if hasattr(test, key):
                setattr(test, key, value)

        await self.session.commit()

        return test
