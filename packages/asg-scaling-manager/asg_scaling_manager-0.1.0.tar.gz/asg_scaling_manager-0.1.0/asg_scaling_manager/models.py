"""Domain models for ASG Scaling Manager.

These pydantic models define typed structures passed between the selector,
planner, and AWS client. They are intentionally small and explicit to keep
the orchestration code readable and testable.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class AsgInfo(BaseModel):
    """Minimal information about an Auto Scaling Group used by this tool."""

    name: str = Field(..., description="ASG name")
    min_size: int = Field(..., ge=0)
    max_size: int = Field(..., ge=0)
    desired_capacity: int = Field(..., ge=0)


class CapacityUpdate(BaseModel):
    """Desired capacity settings to apply to a single ASG.

    Any field set to None means "do not change" for that attribute.
    """

    name: str
    desired: Optional[int] = Field(None, ge=0)
    min_size: Optional[int] = Field(None, ge=0)
    max_size: Optional[int] = Field(None, ge=0)


class Plan(BaseModel):
    """A full execution plan across multiple ASGs."""

    updates: list[CapacityUpdate]

    @property
    def total_desired(self) -> int:
        return sum(u.desired or 0 for u in self.updates)


