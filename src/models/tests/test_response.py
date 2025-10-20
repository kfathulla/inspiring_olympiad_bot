from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class SubmissionResponse(BaseModel):
    id: int
    text: Optional[str]
    correct_count: int
    incorrect_count: int
    score: float
    user_id: int
    test_id: int

    class Config:
        orm_mode = True


class TestResponse(BaseModel):
    # --- base Test fields ---
    id: int
    user_id: int
    name: Optional[str]
    is_show_correct_count: bool
    is_show_incorrects: bool
    is_show_answers: bool
    is_finished: bool
    finished_at: datetime
    is_public: bool

    # --- aggregated fields ---
    submissions_count: int                # total submissions (all users)
    user_submission: Optional[SubmissionResponse]  # submission of current user (or None)

    class Config:
        orm_mode = True


class TestsResponse(BaseModel):
    tests: list[TestResponse]
    
    class Config:
        orm_mode = True