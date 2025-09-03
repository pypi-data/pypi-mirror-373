from typing import Optional
from pydantic import BaseModel, Field


class ScoreResponse(BaseModel):
    """
    Response model for evaluation scores.
    """

    score: Optional[float] = Field(
        None,
        description="Evaluation score between 0 and 1. If null, the criteria was deemed not applicable.",
    )
    explanation: str = Field(description="Explanation of the evaluation score")


class BinaryEvaluationResponse(BaseModel):
    """
    Response model for binary evaluation results.
    """

    passed: Optional[bool] = Field(
        ...,
        description="Whether the evaluation passed. If null, the criteria was deemed not applicable.",
    )
    explanation: str = Field(None, description="Explanation of the evaluation score")
