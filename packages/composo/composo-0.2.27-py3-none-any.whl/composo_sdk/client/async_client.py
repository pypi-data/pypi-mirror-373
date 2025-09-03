"""
Asynchronous Composo client

This module provides an asynchronous Composo client for high-performance batch evaluation of chat messages.
Composo is an AI evaluation platform that can analyze chat conversations and tool calls,
and provide scores and explanations based on specified criteria.

Main features:
- Asynchronously evaluate chat message quality and relevance
- Support concurrent evaluation of multiple criteria, improving performance
- Handle tool calls and system messages
- Provide retry mechanisms and error handling
- Support connection pooling and concurrency control
"""

import asyncio
from typing import List, Dict, Any, Optional, Union
from .base import BaseClient
from .types import MessagesType, ToolsType, ResultType
from ..models import EvaluationResponse, BinaryEvaluationResponse
from tenacity import stop_after_attempt, wait_exponential, wait_random, AsyncRetrying


class AsyncComposo(BaseClient):
    """Asynchronous Composo client for high-performance batch evaluations.

    This client is used for asynchronous calls to the Composo API for message evaluation.
    Suitable for large batch evaluation scenarios, improving performance through concurrent processing.

    Key features:
        - Asynchronous API calls, supporting high concurrency
        - Automatic retry mechanism, improving request success rate
        - Support for context managers, automatic resource management
        - Concurrency control, preventing excessive requests
        - Support for multiple evaluation criteria
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://platform.composo.ai",
        num_retries: int = 1,
        model_core: Optional[str] = None,
        max_concurrent_requests: int = 5,
        timeout: float = 60.0,
    ):
        """Initialize asynchronous Composo client.

        Args:
            api_key: Composo API key for authentication.
                If not provided, will be loaded from the COMPOSO_API_KEY environment variable.
                Required for all API requests - get from your Composo dashboard.
            base_url: API base URL, defaults to official platform address.
                Change only if using a custom Composo deployment.
            num_retries: Number of retries on request failure, defaults to 1.
                Each retry uses exponential backoff with jitter.
                Set to 0 to disable retries.
            model_core: Optional model core identifier for specifying evaluation model.
                If not provided, uses the default evaluation model.
            max_concurrent_requests: Maximum concurrent requests, defaults to 5.
                Controls the number of simultaneous API requests to prevent overloading.
                Higher values improve throughput but may hit rate limits.
                Recommended: 5-10 for most use cases, 20+ for high-performance scenarios.
            timeout: Request timeout in seconds, defaults to 60 seconds.
                Total time to wait for a single request (including retries).
                Increase for slower networks or complex evaluations.
        """
        super().__init__(api_key, base_url, num_retries, model_core, timeout)
        self.max_concurrent_requests = max_concurrent_requests
        self._semaphore = asyncio.Semaphore(max_concurrent_requests)

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - close HTTP client"""
        await self.aclose()

    async def _make_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make async HTTP request with retry logic using tenacity"""
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(self.num_retries),
            wait=wait_exponential(multiplier=1, min=1, max=60)
            + wait_random(
                0, 1
            ),  # multiplier = 1 means 2x the wait time for each attempt
            reraise=True,
        ):
            with attempt:
                return await self._apost(
                    endpoint="/api/v1/evals/reward",
                    data=request_data,
                    headers=self._build_headers(),
                )

    async def _make_binary_request(
        self, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make async binary evaluation HTTP request with retry logic"""

        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(self.num_retries),
            wait=wait_exponential(multiplier=1, min=1, max=60)
            + wait_random(
                0, 1
            ),  # multiplier = 1 means 2x the wait time for each attempt
            reraise=True,  # re-raise the exception if the request fails
        ):
            with attempt:
                return await self._apost(
                    endpoint="/api/v1/evals/binary",
                    data=request_data,
                    headers=self._build_headers(),
                )

    async def _evaluate_single_criterion(
        self,
        messages: MessagesType,
        system: Optional[str],
        tools: ToolsType,
        result: ResultType,
        single_criterion: str,
    ) -> EvaluationResponse:
        """Evaluate a single criterion with semaphore control"""
        async with self._semaphore:
            evaluation_request = self._prepare_evaluation_request(
                messages, system, tools, result, single_criterion
            )
            request_data = evaluation_request.model_dump(exclude_none=True)

            # Check if this is binary evaluation
            if self._is_binary_criteria(single_criterion):
                response_data = await self._make_binary_request(request_data)
                # Convert binary response to score format
                binary_response = BinaryEvaluationResponse(**response_data)
                score = 1.0 if binary_response.passed else 0.0
                return EvaluationResponse(
                    score=score, explanation=binary_response.explanation
                )
            else:
                response_data = await self._make_request(request_data)
                return EvaluationResponse.from_dict(response_data)

    async def _evaluate_multiple_criteria(
        self,
        messages: MessagesType,
        system: Optional[str],
        tools: ToolsType,
        result: ResultType,
        criteria: List[str],
    ) -> List[EvaluationResponse]:
        """Evaluate multiple criteria concurrently"""
        tasks = [
            self._evaluate_single_criterion(
                messages, system, tools, result, single_criterion
            )
            for single_criterion in criteria
        ]
        return await asyncio.gather(*tasks)

    async def evaluate(
        self,
        messages: MessagesType,
        system: Optional[str] = None,
        tools: ToolsType = None,
        result: ResultType = None,
        criteria: Optional[Union[str, List[str]]] = None,
    ) -> Union[EvaluationResponse, List[EvaluationResponse]]:
        """Asynchronously evaluate messages with optional criteria.

        Args:
            messages: List of chat messages to evaluate.
                Format: [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hello!"}]
            system: Optional system message to set AI behavior and context.
            tools: Optional list of tool definitions for evaluating tool calls.
            result: Optional LLM result to append to the conversation.
            criteria: Optional evaluation criteria (str or list of str).

        Returns:
            EvaluationResponse or list of EvaluationResponse objects.
        """

        # Convert single criteria to list if needed
        if isinstance(criteria, str):
            criteria = [criteria]

        # Always evaluate multiple criteria
        results = await self._evaluate_multiple_criteria(
            messages, system, tools, result, criteria
        )

        # Return single result if only one criteria was provided
        if len(criteria) == 1:
            return results[0]
        else:
            return results
