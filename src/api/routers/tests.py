from fastapi import APIRouter, Form, HTTPException, Depends, Security
from typing import Annotated
from fastapi.responses import JSONResponse
import json
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.api.deps import RepoDep, CurrentUserDep
from src.models.tests import SubmissionResponse, TestResponse, TestsResponse

tests_router = APIRouter(prefix="/api/tests", tags=["tests"])


@tests_router.get("/", response_model=TestsResponse)
async def get_tests(repo: RepoDep, current_user: CurrentUserDep):
    tests = await repo.tests.get_all_tests(current_user.user_id)

    res = TestsResponse(tests=[])

    for test_obj, submissions_count, user_submission_json in tests:
        if user_submission_json is not None:
            user_sub_dict = json.loads(user_submission_json)
            submission_obj = SubmissionResponse(**user_sub_dict)
        else:
            submission_obj = None

        res.tests.append(
            TestResponse(
                id=test_obj.id,
                user_id=test_obj.user_id,
                name=test_obj.name,
                is_show_correct_count=test_obj.is_show_correct_count,
                is_show_incorrects=test_obj.is_show_incorrects,
                is_show_answers=test_obj.is_show_answers,
                is_finished=test_obj.is_finished,
                finished_at=test_obj.finished_at,
                is_public=test_obj.is_public,
                submissions_count=submissions_count,
                user_submission=submission_obj,
            )
        )

    return res
