# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
General Analysis SDK (ga-sdk) is a Python SDK for AI Guardrails that provides a simple and intuitive interface for invoking and managing AI guardrails. The SDK follows the design patterns of OpenAI and Anthropic SDKs, emphasizing simplicity and direct mapping to the REDit-server backend API.

## Development Commands

### Install dependencies
```bash
uv pip install -e .[dev]
```

### Code quality tools
```bash
uv run black generalanalysis/       # Format code
uv run ruff check generalanalysis/  # Lint code  
uv run mypy generalanalysis/        # Type check
```

### Run examples
```bash
uv run python examples/basic_usage.py
```

## Architecture

### Design Philosophy
This SDK is designed to be minimal and directly mirror the REDit-server implementation without extra features or convenience methods. Every feature should have a corresponding server endpoint.

### Core Components

**Client Structure** (`client.py`, `async_client.py`)
- Two client types: synchronous (`Client`) and asynchronous (`AsyncClient`)
- Both follow resource-based patterns where operations are grouped under `client.guards.*`
- Authentication via Bearer token from env var: `GA_API_KEY`
- Base URL defaults to `https://art-server.generalanalysis.com`

**HTTP Layer** (`core/http_client.py`)
- `BaseHTTPClient`: Shared logic for headers, URL building, error handling
- `SyncHTTPClient`: Uses `requests` library for synchronous operations
- `AsyncHTTPClient`: Uses `httpx` library for async operations
- Handles authentication errors (401), guard not found (404), and generic API errors

**Type System** (`types/`)
- All models use Pydantic v2 with `model_config` pattern
- Field aliases handle server response differences (e.g., `block` → `blocked`)
- Models directly map to server schemas without extra properties

**API Endpoints** (implemented in `resources/guards.py` and `resources/async_guards.py`)
- `GET /guards` - List all guards
- `GET /guards/{id}` - Get guard details
- `POST /guards/invoke` - Invoke guard with text
- `GET /guards/generate-policies-from-job/{job_id}` - Generate policies from job
- `GET /guards/logs` - List guard invocation logs (paginated)

### Key Server Mappings

The SDK models map directly to server responses:
- `GuardInvokeResult.blocked` maps from server's `block` field
- `PolicyEvaluation.passed` maps from server's `pass` field  
- No convenience properties or computed fields are added

## Important Constraints

- **No speculative features**: Only implement what exists in the REDit-server
- **Minimal exceptions**: Only `GeneralAnalysisError`, `AuthenticationError`, and `GuardNotFoundError`
- **No test suite**: Keep the package simple and focused
- **Direct field mapping**: Use Pydantic aliases for server differences, don't add computed properties