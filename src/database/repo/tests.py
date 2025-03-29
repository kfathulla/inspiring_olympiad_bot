from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.database.models.tests import Test
from src.database.repo.base import BaseRepo


class TestRepo(BaseRepo):
    async def insert_test(self, test: Test): 
        self.session.add(test)
         
        await self.session.commit()
        return await self.session.get(
            Test,
            test.id,
            options=[selectinload(Test.test_answers)]
        )
    
    async def get_test_by_id(self, id):
        stmt = select(Test).options(selectinload(Test.test_answers)).where(Test.id == id)
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