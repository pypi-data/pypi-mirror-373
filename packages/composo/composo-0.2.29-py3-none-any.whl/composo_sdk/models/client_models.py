from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field


class EvaluationRequest(BaseModel):
    """
    Client-side evaluation request model used by the SDK clients.
    """

    messages: List[Dict[str, Any]] = Field(..., description="A list of chat messages")
    system_message: Optional[str] = Field(
        None, description="System message for the evaluation"
    )
    tools: Optional[List[Dict[str, Any]]] = Field(
        None, description="Tools available for the evaluation"
    )
    evaluation_criteria: Optional[Union[str, List[str]]] = Field(
        None, description="Evaluation criteria"
    )
    model_core: Optional[str] = Field(None, description="The model core for evaluation")


class EvaluationResponse(BaseModel):
    """
    Client-side evaluation response model used by the SDK clients.
    """

    score: Optional[float] = Field(None, description="Evaluation score between 0 and 1")
    explanation: str = Field(description="Explanation of the evaluation result")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvaluationResponse":
        """Create EvaluationResponse from dictionary"""
        return cls(**data)
