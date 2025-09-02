"""Guard-related type definitions."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class GuardPolicy(BaseModel):
    """Represents a policy associated with a guard."""

    id: int
    name: str
    definition: str


class Guard(BaseModel):
    """Represents a guard configuration."""

    id: int
    name: str
    description: str
    hf_id: Optional[str] = None
    endpoint: str
    system_prompt: Optional[str] = None
    policies: List[GuardPolicy] = Field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump()

    def to_json(self, **kwargs: Any) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(**kwargs)


class PolicyEvaluation(BaseModel):
    """Represents the evaluation result of a single policy."""

    model_config = {"populate_by_name": True}

    name: str
    definition: str
    passed: bool = Field(alias="pass")
    violation_prob: float


class GuardInvokeResult(BaseModel):
    """Represents the result of invoking a guard."""

    block: bool
    latency_ms: float
    policies: List[PolicyEvaluation]
    raw: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump()

    def to_json(self, **kwargs: Any) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(**kwargs)


class GuardLog(BaseModel):
    """Represents a guard invocation log entry."""

    id: int
    user_id: str
    guard_id: int
    input_text: str
    result: Union[Dict[str, Any], List[Dict[str, Any]]]
    latency_ms: float
    blocked: bool
    created_at: datetime
    policies: List[GuardPolicy] = Field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump()

    def to_json(self, **kwargs: Any) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(**kwargs)


class PaginatedLogsResponse(BaseModel):
    """Represents a paginated response for guard logs."""

    items: List[GuardLog]
    total: int
    page: int
    page_size: int
    total_pages: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump()

    def to_json(self, **kwargs: Any) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(**kwargs)
