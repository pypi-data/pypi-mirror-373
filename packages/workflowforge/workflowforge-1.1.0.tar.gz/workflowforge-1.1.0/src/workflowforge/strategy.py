"""Strategy and matrix definitions for jobs."""

from typing import Any

from pydantic import BaseModel, Field


class Matrix(BaseModel):
    """Represents a build matrix."""

    model_config = {"extra": "allow"}

    include: list[dict[str, Any]] | None = Field(
        None, description="Additional configurations"
    )
    exclude: list[dict[str, Any]] | None = Field(
        None, description="Configurations to exclude"
    )

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """Serialize matrix including dynamic variables."""
        result = super().model_dump(**kwargs)
        return {k: v for k, v in result.items() if v is not None}


class Strategy(BaseModel):
    """Represents execution strategy for jobs."""

    matrix: Matrix | None = Field(None, description="Configuration matrix")
    fail_fast: bool | None = Field(None, description="Fail fast on error")
    max_parallel: int | None = Field(None, description="Maximum parallel jobs")

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """Serialize strategy."""
        result: dict[str, Any] = {}

        if self.matrix:
            result["matrix"] = self.matrix.model_dump(**kwargs)
        if self.fail_fast is not None:
            result["fail-fast"] = self.fail_fast
        if self.max_parallel is not None:
            result["max-parallel"] = self.max_parallel

        return result


# Factory functions for convenient strategy creation
def matrix(**variables: Any) -> Matrix:
    """Create a Matrix conveniently."""
    return Matrix(**variables)


def strategy(
    matrix: Matrix | None = None,
    fail_fast: bool | None = None,
    max_parallel: int | None = None,
) -> Strategy:
    """Create a Strategy conveniently."""
    return Strategy(matrix=matrix, fail_fast=fail_fast, max_parallel=max_parallel)
