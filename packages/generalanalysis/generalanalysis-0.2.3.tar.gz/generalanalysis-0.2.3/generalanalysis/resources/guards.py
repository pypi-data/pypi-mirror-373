"""Guards resource for synchronous operations."""

from typing import List, Optional

from ..core.http_client import SyncHTTPClient
from ..exceptions import GeneralAnalysisError, GuardNotFoundError
from ..types import (
    Guard,
    GuardInvokeResult,
    PaginatedLogsResponse,
    PolicyItem,
)


class Guards:
    """Synchronous guards resource."""

    def __init__(self, client: SyncHTTPClient):
        self._client = client

    def list(self) -> List[Guard]:
        """List all available guards."""
        response = self._client.get("/guards")
        guards_data = response if isinstance(response, list) else [response]
        return [Guard(**guard) for guard in guards_data]

    def get(self, guard_id: int) -> Guard:
        """Get details of a specific guard."""
        try:
            response = self._client.get(f"/guards/{guard_id}")
            return Guard(**response)
        except GeneralAnalysisError as e:
            if e.status_code == 404:
                raise GuardNotFoundError(guard_id) from e
            raise

    def invoke(self, guard_id: int, text: str) -> GuardInvokeResult:
        """Invoke a guard to check text for policy violations."""
        try:
            response = self._client.post(
                "/guards/invoke", data={"guard_id": guard_id, "text": text}
            )
            return GuardInvokeResult(**response)
        except GeneralAnalysisError as e:
            if e.status_code == 404:
                raise GuardNotFoundError(guard_id) from e
            raise

    def generate_policies_from_job(self, job_id: int) -> List[PolicyItem]:
        """Generate policies from successful attack results in a job."""
        response = self._client.get(f"/guards/generate-policies-from-job/{job_id}")
        policies_data = response if isinstance(response, list) else [response]
        return [PolicyItem(**policy) for policy in policies_data]

    def list_logs(
        self, guard_id: Optional[int] = None, page: int = 1, page_size: int = 50
    ) -> PaginatedLogsResponse:
        """List guard invocation logs."""
        params = {"page": page, "page_size": page_size}
        if guard_id is not None:
            params["guard_id"] = guard_id

        response = self._client.get("/guards/logs", params=params)
        return PaginatedLogsResponse(**response)
