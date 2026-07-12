from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from .contracts import GeneratedCode, ImplementationPlan, ReviewResult, TestResult


class SharedState(BaseModel):
    request_id: str
    user_request: str
    plan: ImplementationPlan | None = None
    code: GeneratedCode | None = None
    review: ReviewResult | None = None
    tests: TestResult | None = None
    metadata: dict = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def update_plan(self, plan):
        self.plan = plan
        self.updated_at = __import__("datetime").datetime.utcnow()

    def update_code(self, code):
        self.code = code
        self.updated_at = __import__("datetime").datetime.utcnow()

    def update_review(self, review):
        self.review = review
        self.updated_at = __import__("datetime").datetime.utcnow()

    def update_tests(self, tests):
        self.tests = tests
        self.updated_at = __import__("datetime").datetime.utcnow()
