from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repo.submissions import SubmissionRepo
from src.database.repo.test_answers import TestAnswerRepo
from src.database.repo.tests import TestRepo
from src.database.repo.submitted_answers import SubmittedAnswerRepo
from src.database.repo.users import UserRepo
from src.database.setup import create_engine


@dataclass
class RequestsRepo:
    """
    Repository for handling database operations. This class holds all the repositories for the database models.

    You can add more repositories as properties to this class, so they will be easily accessible.
    """

    session: AsyncSession

    @property
    def users(self) -> UserRepo:
        """
        The User repository sessions are required to manage user operations.
        """
        return UserRepo(self.session)

    @property
    def tests(self) -> TestRepo:
        """
        The Test repository sessions are required to manage test operations.
        """
        return TestRepo(self.session)

    @property
    def test_answers(self) -> TestAnswerRepo:
        """
        The TestAnswer repository repository sessions are required to manage test answer operations.
        """
        return TestAnswerRepo(self.session)

    @property
    def submissions(self) -> SubmissionRepo:
        """
        The Submission repository sessions are required to manage submission operations.
        """
        return SubmissionRepo(self.session)

    @property
    def submitted_answers(self) -> SubmittedAnswerRepo:
        """
        The Submission repository sessions are required to manage submission operations.
        """
        return SubmittedAnswerRepo(self.session)

if __name__ == "__main__":
    from src.database.setup import create_session_pool
    from src.config import Config

    async def example_usage(config: Config):
        """
        Example usage function for the RequestsRepo class.
        Use this function as a guide to understand how to utilize RequestsRepo for managing user data.
        Pass the config object to this function for initializing the database resources.
        :param config: The config object loaded from your configuration.
        """
        engine = create_engine(config.db)
        session_pool = create_session_pool(engine)

        async with session_pool() as session:
            repo = RequestsRepo(session)

            # Replace user details with the actual values
            user = await repo.users.get_or_create_user(
                user_id=12356,
                full_name="Fatkhulla",
                username="k_fathulla",
            )