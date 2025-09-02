"""Policy-related type definitions."""

from pydantic import BaseModel


class PolicyItem(BaseModel):
    """Represents a policy item generated from attack analysis."""

    policy_name: str
    policy_description: str
