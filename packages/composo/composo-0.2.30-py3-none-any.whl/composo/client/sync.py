"""
Synchronous Composo client

This module provides a synchronous Composo client for evaluating chat message quality.
Composo is an AI evaluation platform that can analyze chat conversations and tool calls,
and provide scores and explanations based on specified criteria.

Main features:
- Evaluate chat message quality and relevance
- Support multiple evaluation criteria (single or multiple criteria)
- Handle tool calls and system messages
- Provide retry mechanisms and error handling
"""

from typing import List, Dict, Any, Optional, Union
from .base import BaseClient
from .types import MessagesType, ToolsType, ResultType
from ..models import EvaluationResponse, BinaryEvaluationResponse
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    wait_random,
    retry_if_exception_type,
)


class Composo(BaseClient):
    """Synchronous Composo client.

    This client is used for synchronous calls to the Composo API for message evaluation.
    Suitable for single evaluations or small batch evaluation scenarios, providing a simple and easy-to-use interface.

    Key features:
        - Synchronous API calls, easy to integrate into existing code
        - Automatic retry mechanism, improving request success rate
        - Support for context managers, automatic resource management
        - Support for multiple evaluation criteria

    Inherits from BaseClient, which provides:
        - api_key: Composo API key for authentication
        - base_url: API base URL, defaults to official platform address
        - num_retries: Number of retries on request failure, defaults to 1
        - model_core: Optional model core identifier for specifying evaluation model
        - timeout: Request timeout in seconds, defaults to 60 seconds
    """

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close HTTP client"""
        self.close()

    def _make_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request with retry logic using tenacity (exponential backoff base 2 + jitter)"""

        @retry(
            stop=stop_after_attempt(self.num_retries),
            wait=wait_exponential(multiplier=1, min=1, max=60) + wait_random(0, 1),
            retry=retry_if_exception_type(Exception),
            reraise=True,
        )
        def do_request():
            return self._post(
                endpoint="/api/v1/evals/reward",
                data=request_data,
                headers=self._build_headers(),
            )

        return do_request()

    def _make_binary_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make binary evaluation HTTP request with retry logic"""

        @retry(
            stop=stop_after_attempt(self.num_retries),
            wait=wait_exponential(multiplier=1, min=1, max=60) + wait_random(0, 1),
            retry=retry_if_exception_type(Exception),
            reraise=True,
        )
        def do_request():
            return self._post(
                endpoint="/api/v1/evals/binary",
                data=request_data,
                headers=self._build_headers(),
            )

        return do_request()

    def _evaluate_single_criterion(
        self,
        messages: MessagesType,
        system: Optional[str],
        tools: ToolsType,
        result: ResultType,
        single_criterion: str,
    ) -> EvaluationResponse:
        """Evaluate a single criterion synchronously"""
        evaluation_request = self._prepare_evaluation_request(
            messages, system, tools, result, single_criterion
        )
        request_data = evaluation_request.model_dump(exclude_none=True)

        # Check if this is binary evaluation
        if self._is_binary_criteria(single_criterion):
            response_data = self._make_binary_request(request_data)
            # Convert binary response to score format
            binary_response = BinaryEvaluationResponse(**response_data)
            score = 1.0 if binary_response.passed else 0.0
            return EvaluationResponse(
                score=score, explanation=binary_response.explanation
            )
        else:
            response_data = self._make_request(request_data)
            return EvaluationResponse.from_dict(response_data)

    def evaluate(
        self,
        messages: MessagesType,
        system: Optional[str] = None,
        tools: ToolsType = None,
        result: ResultType = None,
        criteria: Optional[Union[str, List[str]]] = None,
    ) -> Union[EvaluationResponse, List[EvaluationResponse]]:
        """Evaluate messages with optional criteria.

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
        results = self._evaluate_multiple_criteria(
            messages, system, tools, result, criteria
        )

        # Return single result if only one criteria was provided
        if len(criteria) == 1:
            return results[0]
        else:
            return results

    def _evaluate_multiple_criteria(
        self,
        messages: MessagesType,
        system: Optional[str],
        tools: ToolsType,
        result: ResultType,
        criteria: List[str],
    ) -> List[EvaluationResponse]:
        """Evaluate multiple criteria sequentially"""
        results = []
        for single_criterion in criteria:
            results.append(
                self._evaluate_single_criterion(
                    messages, system, tools, result, single_criterion
                )
            )
        return results
