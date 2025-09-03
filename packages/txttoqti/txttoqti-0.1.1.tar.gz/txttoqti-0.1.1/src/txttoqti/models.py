"""
Data models for the txttoqti package.

Defines the core data structures used throughout the conversion process.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class QuestionType(Enum):
    """Supported question types."""
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"
    FILL_IN_BLANK = "fill_in_blank"


@dataclass
class Choice:
    """Represents a choice in a multiple choice question."""
    id: str
    text: str
    is_correct: bool = False
    feedback: Optional[str] = None


@dataclass
class Question:
    """
    Represents a single question in the question bank.
    
    This is the core data structure used throughout the conversion process.
    """
    id: str
    text: str
    question_type: QuestionType
    choices: List[Choice] = field(default_factory=list)
    correct_answer: Optional[str] = None
    points: float = 1.0
    feedback: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Validate question data after initialization."""
        if not self.text.strip():
            raise ValueError("Question text cannot be empty")
        
        if self.question_type == QuestionType.MULTIPLE_CHOICE and not self.choices:
            raise ValueError("Multiple choice questions must have choices")
        
        if self.points < 0:
            raise ValueError("Points must be non-negative")

    def get_correct_choices(self) -> List[Choice]:
        """Get all correct choices for this question."""
        return [choice for choice in self.choices if choice.is_correct]

    def add_choice(self, text: str, is_correct: bool = False, feedback: Optional[str] = None) -> Choice:
        """
        Add a choice to this question.
        
        Args:
            text: Choice text
            is_correct: Whether this choice is correct
            feedback: Optional feedback for this choice
            
        Returns:
            The created choice
        """
        choice_id = f"{self.id}_choice_{len(self.choices) + 1}"
        choice = Choice(id=choice_id, text=text, is_correct=is_correct, feedback=feedback)
        self.choices.append(choice)
        return choice


@dataclass
class Assessment:
    """Represents a complete assessment/quiz."""
    id: str
    title: str
    questions: List[Question] = field(default_factory=list)
    description: Optional[str] = None
    time_limit: Optional[int] = None  # in minutes
    attempts_allowed: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_question(self, question: Question) -> None:
        """Add a question to this assessment."""
        self.questions.append(question)
    
    def get_total_points(self) -> float:
        """Calculate total points for this assessment."""
        return sum(q.points for q in self.questions)
    
    def get_question_count(self) -> int:
        """Get the number of questions in this assessment."""
        return len(self.questions)