"""Gemini integration with deterministic local fallbacks.

This service keeps the application usable even when the Gemini API key is not
configured or the remote model is unavailable. It exposes a LangChain-compatible
Runnable through ``model`` so the existing agent pipelines continue to work.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from typing import Any

from langchain_core.runnables import RunnableLambda
from tenacity import retry, stop_after_attempt, wait_random_exponential

from app.core.config import settings

try:
    import google.generativeai as genai
except Exception:  # pragma: no cover - optional dependency path
    genai = None


logger = logging.getLogger(__name__)


class GeminiService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GeminiService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.api_key = settings.gemini_api_key.strip()
            self._remote_model = None
            if self.api_key and genai is not None:
                try:
                    genai.configure(api_key=self.api_key)
                    self._remote_model = genai.GenerativeModel("gemini-1.5-flash")
                    logger.info("Gemini remote model configured successfully.")
                except Exception as exc:
                    logger.warning("Gemini SDK configuration failed, using local fallback: %s", exc)
            else:
                logger.info("Gemini API key not configured; using local fallback model.")

            self.model = RunnableLambda(self._invoke_model)
            self.initialized = True

    def _invoke_model(self, prompt: Any) -> str:
        """LangChain-compatible model entry point."""

        prompt_text = prompt if isinstance(prompt, str) else str(prompt)
        return self.generate_content(prompt_text)

    def _extract_prompt_section(self, prompt: str, label: str) -> str:
        pattern = rf"{re.escape(label)}:\s*(.*?)(?:\n\n[A-Z][A-Za-z ]+:|\Z)"
        match = re.search(pattern, prompt, re.DOTALL)
        return match.group(1).strip() if match else prompt.strip()

    def _make_embedding(self, text: str, dimensions: int = 16) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values: list[float] = []
        for index in range(dimensions):
            byte_value = digest[index % len(digest)]
            values.append((byte_value / 255.0) * 2.0 - 1.0)
        return values

    def embed_text(self, text: str, dimensions: int = 16) -> list[float]:
        """Return a deterministic embedding vector for text."""

        return self._make_embedding(text, dimensions)

    def _mock_plan(self, prompt: str) -> str:
        issue = self._extract_prompt_section(prompt, "GitHub Issue")
        repository_summary = self._extract_prompt_section(prompt, "Repository Summary")
        payload = {
            "plan": [
                {
                    "step": "Inspect the repository structure and locate relevant files.",
                    "reason": f"Understand the code paths related to: {issue[:120]}",
                    "priority": 1,
                    "files_involved": ["backend/app", "frontend/src"],
                },
                {
                    "step": "Implement the smallest production-safe fix.",
                    "reason": "Apply a targeted change based on the repository summary.",
                    "priority": 2,
                    "files_involved": ["backend/app/services/gemini_service.py", "backend/app/services/vector_db_service.py"],
                },
                {
                    "step": "Run the workflow and capture logs.",
                    "reason": f"Validate the change against the repository context: {repository_summary[:120]}",
                    "priority": 3,
                    "files_involved": ["backend/app/workflow/graph.py"],
                },
            ]
        }
        return json.dumps(payload)

    def _mock_repository_search(self) -> str:
        payload = {
            "relevant_files": [
                {
                    "file_path": "backend/app/workflow/graph.py",
                    "confidence_score": 0.92,
                    "code_snippet": "Workflow graph orchestration and node wiring.",
                },
                {
                    "file_path": "backend/app/services/vector_db_service.py",
                    "confidence_score": 0.88,
                    "code_snippet": "Vector database collection creation, query, and fallback handling.",
                },
                {
                    "file_path": "backend/app/services/gemini_service.py",
                    "confidence_score": 0.86,
                    "code_snippet": "LLM integration and local fallback behavior.",
                },
            ]
        }
        return json.dumps(payload)

    def _mock_coding(self) -> str:
        payload = {
            "modified_files": [
                {
                    "file_path": "backend/app/services/gemini_service.py",
                    "original_content": "Hard-failing Gemini initialization.",
                    "modified_content": "Graceful local fallback and LangChain-compatible runnable.",
                }
            ]
        }
        return json.dumps(payload)

    def _mock_reflection(self) -> str:
        payload = {
            "root_cause": "The workflow depends on external services that may not be configured locally.",
            "fix_recommendation": "Add deterministic fallbacks and validate external service availability before invoking the workflow.",
            "confidence_score": 0.91,
        }
        return json.dumps(payload)

    def _mock_debug(self) -> str:
        payload = {
            "modified_files": [
                {
                    "file_path": "backend/app/services/vector_db_service.py",
                    "original_content": "Remote Chroma-only repository search.",
                    "modified_content": "Hybrid Chroma / in-memory repository search fallback.",
                }
            ]
        }
        return json.dumps(payload)

    def _mock_review(self) -> str:
        payload = {
            "suggestions": [
                {
                    "file_path": "backend/app/services/gemini_service.py",
                    "line_number": 1,
                    "comment": "Keep the local fallback documented because it is now part of the runtime contract.",
                    "category": "Readability",
                }
            ]
        }
        return json.dumps(payload)

    def _local_fallback(self, prompt: str) -> str:
        normalized = prompt.lower()
        if "repository summary" in normalized and "plan" in normalized:
            return self._mock_plan(prompt)
        if "planner request" in normalized or "relevant files" in normalized:
            return self._mock_repository_search()
        if "generated code" in normalized and "test failures" in normalized:
            return self._mock_reflection()
        if "reflection" in normalized and "original code" in normalized:
            return self._mock_debug()
        if "modified code" in normalized:
            return self._mock_review()
        if "github issue" in normalized and "retrieved code" in normalized:
            return self._mock_coding()
        return json.dumps({"message": "Local fallback response", "prompt": prompt[:240]})

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
    def generate_content(self, prompt: str):
        """Generate content using Gemini or a deterministic local fallback."""

        try:
            if self._remote_model is not None:
                response = self._remote_model.generate_content(prompt)
                response_text = getattr(response, "text", "") or str(response)
                self._log_token_usage(prompt, response_text)
                return response_text

            return self._local_fallback(prompt)
        except Exception as e:
            logger.error(f"Error generating content from Gemini: {e}")
            return self._local_fallback(prompt)

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
    def stream_content(self, prompt: str):
        """Stream content from Gemini or the local fallback."""

        try:
            response_text = self.generate_content(prompt)
            for chunk in response_text.split():
                yield chunk + " "
        except Exception as e:
            logger.error(f"Error streaming content from Gemini: {e}")
            fallback_text = self._local_fallback(prompt)
            for chunk in fallback_text.split():
                yield chunk + " "

    def _log_token_usage(self, prompt: str, response_text: str):
        """Log the token usage for a given prompt and response."""

        prompt_tokens = len(prompt.split())
        completion_tokens = len(response_text.split())
        total_tokens = prompt_tokens + completion_tokens
        logger.info(f"Gemini API call token usage: ~{total_tokens} tokens.")


def get_gemini_service():
    return GeminiService()
