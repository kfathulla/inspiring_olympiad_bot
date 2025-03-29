from sqlalchemy import select

from src.database.models.test_answers import TestAnswer
from src.database.repo.base import BaseRepo


class TestAnswerRepo(BaseRepo):
    async def add_test_answer(self, test_answer: TestAnswer): 
        self.session.add(test_answer)
         
        await self.session.commit()
        return await self.session.get(TestAnswer, test_answer.id)
    
    async def get_test_answer_by_id(self, id):
        stmt = select(TestAnswer).where(TestAnswer.id == id)
        result = await self.session.execute(stmt)
        
        return result.scalar_one_or_none()

    async def get_test_answers_by_test(self, test_id: int):
        stmt = select(TestAnswer).where(TestAnswer.test_id == test_id)
        result = await self.session.execute(stmt)
        
        return result.scalars().all()

    async def update_test_answer(self, test_answer: TestAnswer, **kwargs):
        for key, value in kwargs.items():
            if hasattr(test_answer, key):
                setattr(test_answer, key, value)
                
        await self.session.commit()

        return test_answer