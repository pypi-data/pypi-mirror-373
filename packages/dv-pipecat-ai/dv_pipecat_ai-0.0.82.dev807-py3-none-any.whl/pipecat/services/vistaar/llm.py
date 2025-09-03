"""Vistaar LLM Service implementation."""

import asyncio
import json
import time
import uuid
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Dict, Optional
from urllib.parse import urlencode

import httpx
from loguru import logger
from pydantic import BaseModel, Field

from pipecat.frames.frames import (
    Frame,
    LLMFullResponseEndFrame,
    LLMFullResponseStartFrame,
    LLMMessagesFrame,
    LLMTextFrame,
    LLMUpdateSettingsFrame,
    StartInterruptionFrame,
    StopInterruptionFrame,
)
from pipecat.processors.aggregators.llm_response import (
    LLMAssistantAggregatorParams,
    LLMUserAggregatorParams,
)
from pipecat.processors.aggregators.openai_llm_context import (
    OpenAILLMContext,
    OpenAILLMContextFrame,
)
from pipecat.services.openai.llm import (
    OpenAIAssistantContextAggregator,
    OpenAIContextAggregatorPair,
    OpenAIUserContextAggregator,
)
from pipecat.processors.frame_processor import FrameDirection
from pipecat.services.llm_service import LLMService


class VistaarLLMService(LLMService):
    """A service for interacting with Vistaar's voice API using Server-Sent Events.

    This service handles text generation through Vistaar's SSE endpoint which
    streams responses in real-time. Vistaar maintains all conversation context
    server-side via session_id, so we only send the latest user message.
    """

    class InputParams(BaseModel):
        """Input parameters for Vistaar model configuration.

        Parameters:
            source_lang: Source language code (e.g., 'mr' for Marathi, 'hi' for Hindi).
            target_lang: Target language code for responses.
            session_id: Session ID for maintaining conversation context.
            extra: Additional model-specific parameters.
        """

        source_lang: Optional[str] = Field(default="mr")
        target_lang: Optional[str] = Field(default="mr")
        session_id: Optional[str] = Field(default=None)
        extra: Optional[Dict[str, Any]] = Field(default_factory=dict)

    def __init__(
        self,
        *,
        base_url: str = "https://vistaar.kenpath.ai/api",
        params: Optional[InputParams] = None,
        timeout: float = 30.0,
        **kwargs,
    ):
        """Initialize Vistaar LLM service.

        Args:
            base_url: The base URL for Vistaar API. Defaults to "https://vistaar.kenpath.ai/api".
            params: Input parameters for model configuration and behavior.
            timeout: Request timeout in seconds. Defaults to 30.0 seconds.
            **kwargs: Additional arguments passed to the parent LLMService.
        """
        super().__init__(**kwargs)

        params = params or VistaarLLMService.InputParams()

        self._base_url = base_url.rstrip("/")
        self._source_lang = params.source_lang
        self._target_lang = params.target_lang
        self._session_id = params.session_id or str(uuid.uuid4())
        self._extra = params.extra if isinstance(params.extra, dict) else {}
        self._timeout = timeout

        # Create an async HTTP client
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(self._timeout))

        # Interruption handling state
        self._current_response = None  # Track current HTTP response stream
        self._is_interrupted = False  # Track if current generation was interrupted
        self._partial_response = []  # Track what was actually sent before interruption

        logger.info(
            f"Vistaar LLM initialized - Base URL: {self._base_url}, Session ID: {self._session_id}, Source Lang: {self._source_lang}, Target Lang: {self._target_lang}, Timeout: {self._timeout}s"
        )

    async def _extract_messages_to_query(self, context: OpenAILLMContext) -> str:
        """Extract only the last user message from context.

        Since Vistaar maintains context server-side via session_id,
        we only need to send the most recent user message.

        As a fallback for context synchronization, we can optionally include
        information about interrupted responses.

        Args:
            context: The OpenAI LLM context containing messages.

        Returns:
            The last user message as a query string, optionally with context hints.
        """
        messages = context.get_messages()
        query_parts = []

        # Include interrupted response context as a hint (optional fallback strategy)
        if hasattr(self, "_last_interrupted_response"):
            interrupted_text = self._last_interrupted_response[:100]  # Limit length
            query_parts.append(
                f"[Context: I was previously saying '{interrupted_text}...' when interrupted]"
            )
            # Clear the interrupted response after using it
            delattr(self, "_last_interrupted_response")

        # Find the last user message (iterate in reverse for efficiency)
        for message in reversed(messages):
            if message.get("role") == "user":
                content = message.get("content", "")

                # Handle content that might be a list (for multimodal messages)
                if isinstance(content, list):
                    text_parts = [
                        item.get("text", "") for item in content if item.get("type") == "text"
                    ]
                    content = " ".join(text_parts)

                if isinstance(content, str):
                    query_parts.append(content.strip())
                    break

        # If no user message found, return empty string or just context
        return " ".join(query_parts) if query_parts else ""

    async def _handle_interruption(self):
        """Handle interruption by cancelling ongoing stream."""
        logger.debug("Handling interruption for Vistaar LLM")

        # Set interruption flag
        self._is_interrupted = True

        # Cancel ongoing HTTP response stream if active
        if self._current_response:
            try:
                await self._current_response.aclose()
                logger.debug("Closed active Vistaar response stream")
            except Exception as e:
                logger.warning(f"Error closing Vistaar response stream: {e}")
            finally:
                self._current_response = None

        # Store partial response for potential inclusion in next query
        if self._partial_response:
            partial_text = "".join(self._partial_response)
            logger.debug(f"Storing interrupted response: {partial_text[:100]}...")
            # Store the interrupted response for next query context
            self._last_interrupted_response = partial_text

        # Clear current partial response
        self._partial_response = []

    async def _stream_response(self, query: str) -> AsyncGenerator[str, None]:
        """Stream response from Vistaar API using Server-Sent Events.

        Args:
            query: The user's query to send to the API.

        Yields:
            Text chunks from the streaming response.
        """
        # Prepare query parameters
        params = {
            "query": query,
            "session_id": self._session_id,
            "source_lang": self._source_lang,
            "target_lang": self._target_lang,
        }

        # Add any extra parameters
        params.update(self._extra)

        # Construct the full URL with query parameters
        url = f"{self._base_url}/voice/?{urlencode(params)}"

        logger.info(
            f"Vistaar API request - URL: {self._base_url}/voice/, Session: {self._session_id}, Query: {query[:100]}..."
        )
        logger.debug(f"Full URL with params: {url}")

        # Reset interruption state and partial response for new request
        self._is_interrupted = False
        self._partial_response = []

        try:
            # Use httpx to handle SSE streaming
            async with self._client.stream("GET", url) as response:
                self._current_response = response  # Store for potential cancellation
                response.raise_for_status()

                # Process the SSE stream
                async for line in response.aiter_lines():
                    # Check for interruption before processing each line
                    if self._is_interrupted:
                        logger.debug("Stream interrupted, stopping processing")
                        break

                    if not line:
                        continue

                    self._partial_response.append(line)  # Track what we're sending
                    yield line

        except httpx.HTTPStatusError as e:
            logger.error(
                f"Vistaar HTTP error - Status: {e.response.status_code}, URL: {url}, Response: {e.response.text if hasattr(e.response, 'text') else 'N/A'}"
            )
            raise
        except httpx.TimeoutException as e:
            logger.error(f"Vistaar timeout error - URL: {url}, Timeout: {self._timeout}s")
            raise
        except Exception as e:
            logger.error(
                f"Vistaar unexpected error - Type: {type(e).__name__}, Message: {str(e)}, URL: {url}"
            )
            raise
        finally:
            # Clean up response reference
            self._current_response = None

    async def _process_context(self, context: OpenAILLMContext):
        """Process the LLM context and generate streaming response.

        Args:
            context: The OpenAI LLM context containing messages to process.
        """
        logger.info(f"Vistaar processing context - Session: {self._session_id}")
        try:
            # Extract query from context
            query = await self._extract_messages_to_query(context)

            if not query:
                logger.warning(
                    f"Vistaar: No query extracted from context - Session: {self._session_id}"
                )
                return

            logger.info(f"Vistaar extracted query: {query}")

            logger.debug(f"Processing query: {query[:100]}...")

            # Start response
            await self.push_frame(LLMFullResponseStartFrame())
            await self.start_processing_metrics()
            await self.start_ttfb_metrics()

            first_chunk = True
            full_response = []

            # Stream the response
            async for text_chunk in self._stream_response(query):
                if first_chunk:
                    await self.stop_ttfb_metrics()
                    first_chunk = False

                # Push each text chunk as it arrives
                await self.push_frame(LLMTextFrame(text=text_chunk))
                full_response.append(text_chunk)

            # No need to update context - Vistaar maintains all context server-side
            # The response has already been sent via LLMTextFrame chunks

        except Exception as e:
            logger.error(
                f"Vistaar context processing error - Session: {self._session_id}, Error: {type(e).__name__}: {str(e)}"
            )
            import traceback

            logger.error(f"Vistaar traceback: {traceback.format_exc()}")
            raise
        finally:
            await self.stop_processing_metrics()
            await self.push_frame(LLMFullResponseEndFrame())

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        """Process frames for LLM completion requests.

        Handles OpenAILLMContextFrame, LLMMessagesFrame, and LLMUpdateSettingsFrame
        to trigger LLM completions and manage settings.

        Args:
            frame: The frame to process.
            direction: The direction of frame processing.
        """
        await super().process_frame(frame, direction)
        context = None
        if isinstance(frame, StartInterruptionFrame):
            await self._handle_interruption()
            await self.push_frame(frame, direction)
            return
        elif isinstance(frame, OpenAILLMContextFrame):
            context = frame.context
        elif isinstance(frame, LLMMessagesFrame):
            context = OpenAILLMContext.from_messages(frame.messages)
        elif isinstance(frame, LLMUpdateSettingsFrame):
            # Update settings if needed
            settings = frame.settings
            if "source_lang" in settings:
                self._source_lang = settings["source_lang"]
            if "target_lang" in settings:
                self._target_lang = settings["target_lang"]
            if "session_id" in settings:
                self._session_id = settings["session_id"]
            logger.debug(f"Updated Vistaar settings: {settings}")
        else:
            await self.push_frame(frame, direction)

        if context:
            try:
                await self._process_context(context)
            except httpx.TimeoutException:
                logger.error("Timeout while processing Vistaar request")
                await self._call_event_handler("on_completion_timeout")
            except Exception as e:
                logger.error(f"Error processing Vistaar request: {e}")
                raise

    def create_context_aggregator(
        self,
        context: OpenAILLMContext,
        *,
        user_params: LLMUserAggregatorParams = LLMUserAggregatorParams(),
        assistant_params: LLMAssistantAggregatorParams = LLMAssistantAggregatorParams(),
    ) -> OpenAIContextAggregatorPair:
        """Create context aggregators for Vistaar LLM.

        Since Vistaar uses OpenAI-compatible message format, we reuse OpenAI's
        context aggregators directly, similar to how Groq and Azure services work.

        Args:
            context: The LLM context to create aggregators for.
            user_params: Parameters for user message aggregation.
            assistant_params: Parameters for assistant message aggregation.

        Returns:
            OpenAIContextAggregatorPair: A pair of OpenAI context aggregators,
            compatible with Vistaar's OpenAI-like message format.
        """
        context.set_llm_adapter(self.get_llm_adapter())
        user = OpenAIUserContextAggregator(context, params=user_params)
        assistant = OpenAIAssistantContextAggregator(context, params=assistant_params)
        return OpenAIContextAggregatorPair(_user=user, _assistant=assistant)

    async def close(self):
        """Close the HTTP client when the service is destroyed."""
        await self._client.aclose()

    def __del__(self):
        """Ensure the client is closed on deletion."""
        try:
            asyncio.create_task(self._client.aclose())
        except:
            pass
