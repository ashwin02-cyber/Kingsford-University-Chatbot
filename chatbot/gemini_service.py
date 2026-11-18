import os
import time
import random
import logging
from typing import Generator, List, Dict, Any
from django.conf import settings
from google import genai
from google.genai import types
from google.genai.errors import APIError

from .system_prompt import SYSTEM_PROMPT, LEAKAGE_MARKERS, REFUSAL_MESSAGE

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.api_key = getattr(settings, 'GEMINI_API_KEY', '') or os.getenv('GEMINI_API_KEY', '')
        self.primary_model = getattr(settings, 'GEMINI_MODEL', '') or os.getenv('GEMINI_MODEL', 'gemini-3.5-flash')
        self.fallback_model = getattr(settings, 'GEMINI_FALLBACK_MODEL', '') or os.getenv('GEMINI_FALLBACK_MODEL', 'gemini-3.5-flash-lite')
        self._client = None

    def get_client(self):
        if not self._client:
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY is not configured in backend/.env")
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def _is_transient_error(self, exc: Exception) -> bool:
        """
        Determines if an error is a transient failure (429, 500, 503, 504) per FR-034.
        HTTP 400, 401, 403 are explicitly NOT retried.
        """
        if isinstance(exc, APIError):
            code = getattr(exc, 'code', None) or getattr(exc, 'status_code', None)
            if code in (400, 401, 403):
                return False
            if code in (429, 500, 502, 503, 504):
                return True

        err_str = str(exc).lower()
        if '400' in err_str or '401' in err_str or '403' in err_str or 'permission' in err_str or 'invalid api key' in err_str:
            return False
        if any(code in err_str for code in ['429', '500', '502', '503', '504', 'timeout', 'unavailable', 'resource exhausted']):
            return True

        return False

    def stream_chat_response(
        self,
        contents: List[Dict[str, Any]],
        max_retries: int = 3
    ) -> Generator[str, None, None]:
        """
        Streams AI response from Gemini over SSE with exponential backoff retry and
        fallback model support per FR-032, FR-034, and SEC-003.
        """
        client = self.get_client()

        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.3,
            max_output_tokens=800,
        )

        models_to_try = [self.primary_model]
        if self.fallback_model and self.fallback_model != self.primary_model:
            models_to_try.append(self.fallback_model)

        first_token_received = False
        accumulated_text = ""

        for model_idx, current_model in enumerate(models_to_try):
            is_fallback = model_idx > 0
            if is_fallback:
                logger.warning(f"Switching to fallback model: {current_model}")

            for attempt in range(max_retries + 1):
                try:
                    response_stream = client.models.generate_content_stream(
                        model=current_model,
                        contents=contents,
                        config=config,
                    )

                    for chunk in response_stream:
                        if chunk.text:
                            first_token_received = True
                            accumulated_text += chunk.text

                            # SEC-003: Check for system prompt leakage
                            if any(marker.lower() in accumulated_text.lower() for marker in LEAKAGE_MARKERS):
                                logger.warning("System prompt leakage marker detected. Stopping stream.")
                                yield "\n\n" + REFUSAL_MESSAGE
                                return

                            yield chunk.text

                    # Stream finished successfully
                    return

                except Exception as exc:
                    logger.error(
                        f"Gemini API attempt {attempt + 1}/{max_retries + 1} with {current_model} failed: {type(exc).__name__}: {exc}"
                    )

                    # If token was already yielded, cannot retry stream from scratch
                    if first_token_received:
                        raise exc

                    # If not transient, do not retry
                    if not self._is_transient_error(exc):
                        raise exc

                    # 429 quota exhaustion won't recover in seconds — skip straight to fallback
                    is_quota_exhausted = isinstance(exc, APIError) and (
                        getattr(exc, 'code', None) == 429 or '429' in str(exc)
                    ) and 'quota' in str(exc).lower()

                    if is_quota_exhausted:
                        logger.warning(f"Quota exhausted for {current_model}. Skipping retries, switching to fallback.")
                        break  # skip remaining retries, go to next model

                    # If retry budget remains for this model, wait and retry
                    if attempt < max_retries:
                        backoff = (2 ** attempt) + random.uniform(0.1, 0.5)
                        logger.info(f"Retrying in {backoff:.2f}s...")
                        time.sleep(backoff)
                        continue
                    else:
                        # Exceeded retries for this model
                        if model_idx + 1 < len(models_to_try):
                            logger.info(f"Retries exhausted for {current_model}. Proceeding to fallback.")
                            break  # Breaks inner loop to try next model
                        else:
                            # Both models exhausted
                            raise exc
