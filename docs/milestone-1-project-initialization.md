# Milestone 1: Project Initialization and Folder Structure

## Concept
Set up the foundation for a production-grade autonomous software engineering platform with a clean architecture layout and clear separation of concerns.

## Why this is needed
A multi-agent system grows quickly. Without a disciplined folder structure, the codebase becomes difficult to test, maintain, extend, and deploy.

## Intended structure
- `backend/app/domain`: business entities, repository interfaces, and domain services
- `backend/app/application`: use cases and DTOs
- `backend/app/infrastructure`: GitHub, vector store, cache, and external integrations
- `backend/app/presentation`: API and web-facing adapters
- `frontend/src/features`: feature-level UI modules
- `frontend/src/shared`: reusable UI and shared helpers
- `docs/`: architecture and milestone documentation

## Scope of this milestone
- Initialize the clean-architecture folder skeleton
- Add placeholder files so the structure is tracked in git
- Document the purpose of each layer

## What will come next
Milestone 2 will add the backend core configuration, logging, exception handling, and base dependency injection wiring.
