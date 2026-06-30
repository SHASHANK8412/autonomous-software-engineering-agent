# Milestone 2: Backend Foundation

## Concept
Establish the backend runtime foundation needed for a production system: configuration, structured logging, and consistent exception handling.

## Why this is needed
Agentic systems fail in many places: API calls, database access, external services, and background orchestration. A centralized foundation makes failures observable and easier to debug.

## What was added
- Centralized logging utilities in `backend/app/core/logging.py`
- Centralized exception handling in `backend/app/core/exceptions.py`
- FastAPI bootstrap wiring in `backend/app/main.py`

## Key responsibilities
- `configure_logging()` sets the application-wide log format and root logger level.
- `get_logger()` provides namespaced loggers per module.
- `ApplicationError` defines a reusable application exception shape.
- `register_exception_handlers()` ensures consistent API error responses.

## Scope of this milestone
- Foundation only
- No agent behavior changes yet
- No workflow logic changes yet

## Next milestone
Milestone 3 will add dependency injection, base repository/service abstractions, and the first production-ready application interfaces.