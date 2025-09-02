# GeneralAnalysis Guardrails SDK - Developer Guide

## Quick Start

```python
import generalanalysis

# Initialize client (uses GA_API_KEY environment variable)
client = generalanalysis.Client()

# Invoke a guardrail
result = client.guards.invoke(guard_id=3, text="Contact john@example.com")

# You can use either use result.block for binary decisions or policy.violation_prob for your own tunable threshold-based filtering
if result.block:
    print("Content blocked!")
    for policy in result.policies:
        if not policy.passed:
            print(f"  Violated: {policy.name} - {policy.definition}")
            print(f"  Confidence: {policy.violation_prob:.2%}")
```

## Installation & Setup

```bash
# Install the SDK
pip install generalanalysis

# Set your API key
export GA_API_KEY="your_api_key_here"
```

## Available Guardrails

### 1. **@injection_guard** (ID: 2)
Detects prompt injection and jailbreak attempts.  
**Average Latency:** ~100-150ms

**Policies:**
- `prompt_injection` - Detect prompt injection or jailbreak attempts that try to override or subvert the agent's rules, tools, or scope.

### 2. **@pii_guard** (ID: 3)
Detects personal identifiable information across 16 categories.  
**Average Latency:** ~10-250ms  

**Policies:**
- `PERSON` - Detect names, which can include first names, middle names or initials, and last names.
- `LOCATION` - Detect names of politically or geographically defined locations including cities, provinces, countries, international regions, bodies of water, and mountains.
- `DATE_TIME` - Detect absolute or relative dates, periods, or times smaller than a day.
- `EMAIL_ADDRESS` - Detect email addresses.
- `PHONE_NUMBER` - Detect telephone numbers in various formats.
- `IP_ADDRESS` - Detect IPv4 or IPv6 addresses.
- `CREDIT_CARD` - Detect credit card numbers between 12 to 19 digits.
- `US_BANK_NUMBER` - Detect US bank account numbers between 8 to 17 digits.
- `IBAN_CODE` - Detect International Bank Account Numbers.
- `US_PASSPORT` - Detect US passport number consisting of 9 digits.
- `US_DRIVER_LICENSE` - Detect US driver's license number following state-specific formats according to https://ntsi.com/drivers-license-format/.
- `US_ITIN` - Detect US Individual Taxpayer Identification Number (ITIN) - nine digits that start with "9" and contain "7" or "8" as the 4th digit.
- `URL` - Detect URLs.
- `CRYPTO` - Detect cryptocurrency wallet address. Currently supports Bitcoin addresses.
- `MEDICAL_LICENSE` - Detect common medical license numbers.
- `NRP` - Detect Nationality, Religious or Political group affiliation.

### 3. **@harmfulness_guard** (ID: 4)
Detects harmful content using OpenAI's moderation model.  
**Average Latency:** ~200-500ms  

**Policies:**
- `SEXUAL` - Detect sexually explicit content within the text.
- `VIOLENCE` - Detect explicit or implicit violence within a text.
- `SELF-HARM` - Detect indications of self-harm within a text.
- `HARASSMENT` - Detect harassment or offensive language within a piece of text.
- `ILLEGAL_ACTIVITY` - Detect outputs regarding illegal activities.

### 4. **@intranet_agents_guard** (ID: 6)
Detects out of scope or jailbreak attempts against intranet agents with tools.  
**Average Latency:** ~100-150ms (estimated)

**Policies:**
- `out_of_scope` - Detect and block requests that are outside intranet/company scope or unrelated to supported departments and tools.

## Core Operations

### List Available Guards
```python
guards = client.guards.list() -> List[Guard]
```
Returns a list of all accessible guards with their policies and configurations.

### Get Guard Details
```python
guard = client.guards.get(guard_id: int) -> Guard
```
Returns detailed information about a specific guard including all associated policies.

### Invoke a Guard
```python
result = client.guards.invoke(
    guard_id: int,
    text: str
) -> GuardInvokeResult
```
Checks the provided text against the guard's policies and returns violation results.

### View Invocation Logs
```python
logs = client.guards.list_logs(
    guard_id: Optional[int] = None,  # Filter by guard
    page: int = 1,                   # Page number
    page_size: int = 50              # Items per page (max 100)
) -> PaginatedLogsResponse
```
Returns paginated logs of guard invocations with detailed results.

## Data Types

```python
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

class Guard:
    id: int
    name: str
    description: str
    hf_id: Optional[str]
    endpoint: str
    system_prompt: Optional[str]
    policies: List[GuardPolicy]

class GuardPolicy:
    id: int
    name: str
    definition: str

class GuardInvokeResult:
    block: bool                       # Whether content should be blocked
    latency_ms: float                 # Processing time in milliseconds
    policies: List[PolicyEvaluation]  # Individual policy results
    raw: Dict[str, Any]              # Raw response data from the guard

class PolicyEvaluation:
    name: str                    # Policy identifier (e.g., "EMAIL_ADDRESS")
    definition: str              # Policy description
    passed: bool                 # True if policy check passed (no violation)
    violation_prob: float        # Probability/confidence score (0.0-1.0) of violation

class GuardLog:
    id: int
    user_id: str
    guard_id: int
    input_text: str
    result: Union[Dict[str, Any], List[Dict[str, Any]]]
    latency_ms: float
    blocked: bool
    created_at: datetime
    policies: List[GuardPolicy]

class PaginatedLogsResponse:
    items: List[GuardLog]
    total: int
    page: int
    page_size: int
    total_pages: int

class PolicyItem:
    policy_name: str
    policy_description: str
```

## Async Support

The SDK provides async versions of all methods with identical signatures and return types:

```python
async with generalanalysis.AsyncClient() as client:
    guards = await client.guards.list() -> List[Guard]
    guard = await client.guards.get(guard_id: int) -> Guard
    result = await client.guards.invoke(guard_id: int, text: str) -> GuardInvokeResult
    logs = await client.guards.list_logs(...) -> PaginatedLogsResponse
```

## Error Handling

```python
from generalanalysis import (
    GuardNotFoundError,
    AuthenticationError,
    GeneralAnalysisError
)

try:
    result = client.guards.invoke(guard_id=999, text="test")
except GuardNotFoundError as e:
    print(f"Invalid guard ID: {e}")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except GeneralAnalysisError as e:
    print(f"API error: {e}")
```

## API Reference

**Authentication**: Bearer token via `GA_API_KEY` environment variable

### Methods

| Method | Parameters | Return Type | Description |
|--------|-----------|-------------|-------------|
| `guards.list()` | None | `List[Guard]` | List all accessible guards |
| `guards.get()` | `guard_id: int` | `Guard` | Get specific guard details |
| `guards.invoke()` | `guard_id: int`<br>`text: str` | `GuardInvokeResult` | Check text against guard policies |
| `guards.list_logs()` | `guard_id: Optional[int]`<br>`page: int = 1`<br>`page_size: int = 50` | `PaginatedLogsResponse` | View invocation history |

### Utility Methods

All response objects support:
- `.to_dict()` - Convert to dictionary
- `.to_json(indent=2)` - Convert to formatted JSON string

---
*SDK Version: generalanalysis 0.2.2 | API Version: v1 | Documentation Date: 2025*