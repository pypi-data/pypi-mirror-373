from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic import BaseModel


class Category(BaseModel):
    """
    Represents a single category with its score, reason, keywords, and phrases.
    """

    category: str
    score: int
    reason: str
    keywords: List[str]
    phrases: List[str]


class ScoreResult(BaseModel):
    """
    Represents the overall scoring result, including a list of categories and token counts.
    """

    status: str
    data: List[Category]
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None

    def to_dict(self):
        """
        Converts the ScoreResult object to a dictionary matching the JSON structure.
        """
        return {
            "data": [category.model_dump() for category in self.data],
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
        }


class LLM(ABC):
    @abstractmethod
    def score(self, text: str) -> ScoreResult:
        pass
