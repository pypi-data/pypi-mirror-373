from typing import List, Optional
from pydantic import BaseModel, Field

from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam


class RequestBase(BaseModel):
    messages: List[ChatCompletionMessageParam] = Field(
        ..., description="A list of chat messages", min_items=2
    )
    model_core: Optional[str] = Field(
        None, description="The model core for reward evaluation."
    )


class RewardRequest(RequestBase):
    """
    Request model for reward score evaluation of LLM responses against specified criteria.
    """

    evaluation_criteria: str = Field(
        ...,
        description="Criteria used for evaluation. Begins with 'Reward responses' or 'Penalize responses'",
    )


class BinaryEvaluationRequest(RequestBase):
    """
    Request model for binary evaluation of LLM responses against specified criteria.
    """

    evaluation_criteria: str = Field(
        ...,
        description="Criteria used for evaluation. Begins with 'Response passes if' or 'Response fails if'",
    )
