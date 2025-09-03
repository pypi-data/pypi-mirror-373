import asyncio
import logging
import os
import random
from typing import Optional

from openai import APIError, AsyncAzureOpenAI
from openai._exceptions import APITimeoutError

from .azure_ai_language_utils import TextAnalysis


class AzureOpenAITextAnalyzer:
    """
    Encapsulates an AsyncAzureOpenAI client configured via environment variables,
    and provides a retrying get_text_analysis(...) method.
    """

    # Class‑level defaults
    TRANSIENT_ERROR_CODES = {"DeploymentNotFound", "ServiceUnavailable"}
    MAX_BACKOFF_SECONDS = 60
    DEFAULT_MAX_RETRIES = 10
    DEFAULT_INITIAL_BACKOFF = 1

    def __init__(
        self,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        api_version: Optional[str] = None,
        deployment_name: Optional[str] = None,
    ):
        # Read from env if not provided explicitly
        self.endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT", "")
        self.api_key = api_key or os.getenv("AZURE_OPENAI_KEY", "")
        self.api_version = api_version or os.getenv("AZURE_OPENAI_API_VERSION", "")
        self.deployment_name = deployment_name or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "")

        # Fail fast on mis‑configuration
        if not all([self.endpoint, self.api_key, self.api_version, self.deployment_name]):
            raise RuntimeError(
                "Azure OpenAI configuration error: "
                "AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, AZURE_OPENAI_API_VERSION, "
                "and AZURE_OPENAI_DEPLOYMENT_NAME must all be set."
            )

        # Initialize the async client
        self.client = AsyncAzureOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
            api_version=self.api_version,
        )

        # Logger for this class
        self.logger = logging.getLogger(self.__class__.__name__)

    async def get_text_analysis(
        self,
        system_prompt: str,
        user_prompt: str,
        max_retries: int = DEFAULT_MAX_RETRIES,
        initial_backoff: int = DEFAULT_INITIAL_BACKOFF,
    ) -> Optional[TextAnalysis]:
        """
        Generates a TextAnalysis by calling Azure OpenAI's chat completions.
        Retries on timeouts and specified transient error codes, with jittered exponential backoff.
        """
        last_exception: Optional[Exception] = None
        backoff = initial_backoff

        for attempt in range(1, max_retries + 1):
            try:
                resp = await self.client.beta.chat.completions.parse(
                    model=self.deployment_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    response_format=TextAnalysis,
                )

                choices = getattr(resp, "choices", None) or []
                if not choices:
                    raise RuntimeError("get_text_analysis: Azure returned no choices")

                return choices[0].message.parsed

            except APITimeoutError as e:
                self.logger.warning(
                    "timeout on attempt %d/%d, retrying…",
                    attempt,
                    max_retries,
                    exc_info=e,
                )
                last_exception = e

            except APIError as e:
                code = getattr(e, "code", "") or ""
                if code in self.TRANSIENT_ERROR_CODES:
                    self.logger.warning(
                        "transient APIError '%s' on attempt %d/%d, retrying…",
                        code,
                        attempt,
                        max_retries,
                        exc_info=e,
                    )
                    last_exception = e
                else:
                    self.logger.error("non‑transient APIError '%s', aborting", code, exc_info=e)
                    raise

            except Exception as e:
                self.logger.exception(
                    "unexpected error on attempt %d, aborting", attempt, exc_info=e
                )
                raise

            # backoff before next retry
            if attempt < max_retries:
                sleep_secs = min(backoff, self.MAX_BACKOFF_SECONDS) * (0.5 + random.random() / 2)
                self.logger.info("sleeping %.1fs before next retry", sleep_secs)
                await asyncio.sleep(sleep_secs)
                backoff *= 2
            else:
                self.logger.error("reached max retries (%d), giving up", max_retries)

        # all retries exhausted
        if last_exception:
            raise last_exception
        raise RuntimeError("get_text_analysis: exhausted all retries with no exception details")

    async def close(self) -> None:
        """
        Gracefully close the underlying AsyncAzureOpenAI client.
        """
        await self.client.close()
