from __future__ import annotations
from typing import Optional

from .models.problem_details import ProblemDetails


class ApiException(Exception):
    def __init__(self, problem: ProblemDetails):
        super().__init__(problem.detail or problem.title or "API error")
        self.problem: ProblemDetails = problem

    def __repr__(self) -> str:
        return f"ApiException(status={self.problem.status}, title={self.problem.title!r})"
