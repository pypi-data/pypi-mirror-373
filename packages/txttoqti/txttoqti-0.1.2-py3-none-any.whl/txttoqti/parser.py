"""
parser.py: Text parsing functionality for txttoqti package.

Handles parsing of text files containing questions in various formats
and converts them into structured Question objects.
"""

import re
from typing import List, Optional, Tuple
from .models import Question, QuestionType, Choice
from .exceptions import ParseError
from .logging_config import get_logger


class QuestionParser:
    """
    Parser for extracting questions from text files.

    Supports multiple question formats and converts them into
    structured Question objects for further processing.
    """

    def __init__(self) -> None:
        """Initialize the parser with pattern matching rules."""
        self.logger = get_logger(__name__)
        self.current_question_id = 0
        
        # Regex patterns for different question formats
        self.patterns = {
            'numbered_question': re.compile(r'^\s*(\d+)\.\s*(.+)$'),
            'choice': re.compile(r'^\s*-?\s*([a-d])\)\s*(.+)$', re.IGNORECASE),
            'correct_answer': re.compile(r'^\s*-?\s*Respuesta correcta:\s*([a-d])\s*$', re.IGNORECASE),
            'true_false': re.compile(r'^\s*-?\s*([ab])\)\s*(Verdadero|Falso)\s*$', re.IGNORECASE),
        }

    def parse(self, text: str) -> List[Question]:
        """
        Parse the input text and extract questions.

        Args:
            text: The text content to parse

        Returns:
            List of extracted Question objects

        Raises:
            ParseError: If parsing fails
        """
        try:
            self.logger.info("Starting text parsing")
            lines = [line.rstrip() for line in text.split('\n')]
            questions = []
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    i += 1
                    continue
                
                # Try to parse a question
                question, lines_consumed = self._parse_question_block(lines[i:])
                if question:
                    questions.append(question)
                    i += lines_consumed
                else:
                    i += 1
            
            self.logger.info(f"Parsed {len(questions)} questions")
            return questions
            
        except Exception as e:
            raise ParseError(f"Failed to parse text: {e}")

    def _parse_question_block(self, lines: List[str]) -> Tuple[Optional[Question], int]:
        """
        Parse a block of lines that should contain a complete question.
        
        Args:
            lines: List of lines starting from potential question
            
        Returns:
            Tuple of (Question object or None, number of lines consumed)
        """
        if not lines:
            return None, 0
        
        first_line = lines[0].strip()
        
        # Check if this looks like a numbered question
        match = self.patterns['numbered_question'].match(first_line)
        if not match:
            return None, 1
        
        question_num = match.group(1)
        question_text = match.group(2).strip()
        
        if not question_text:
            return None, 1
        
        self.current_question_id += 1
        question_id = f"q_{self.current_question_id}"
        
        # Start parsing the question and its choices
        lines_consumed = 1
        choices = []
        correct_choice = None
        question_type = QuestionType.MULTIPLE_CHOICE
        
        # Look for choices and correct answer in subsequent lines
        i = 1
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
            
            # Check if this is the start of the next question
            if self.patterns['numbered_question'].match(line):
                break
            
            # Check for choice
            choice_match = self.patterns['choice'].match(line)
            if choice_match:
                choice_id = choice_match.group(1).lower()
                choice_text = choice_match.group(2).strip()
                
                # Check if it's a true/false question
                tf_match = self.patterns['true_false'].match(line)
                if tf_match and choice_text.lower() in ['verdadero', 'falso']:
                    question_type = QuestionType.TRUE_FALSE
                
                choices.append(Choice(
                    id=f"{question_id}_{choice_id}",
                    text=choice_text,
                    is_correct=False
                ))
                i += 1
                lines_consumed += 1
                continue
            
            # Check for correct answer indicator
            correct_match = self.patterns['correct_answer'].match(line)
            if correct_match:
                correct_choice = correct_match.group(1).lower()
                i += 1
                lines_consumed += 1
                continue
            
            # If we can't parse this line, move to next
            i += 1
            lines_consumed += 1
        
        # Mark the correct choice
        if correct_choice:
            for choice in choices:
                if choice.id.endswith(f"_{correct_choice}"):
                    choice.is_correct = True
                    break
        
        # Create the question
        if not choices and question_type == QuestionType.MULTIPLE_CHOICE:
            # If no choices found, treat as short answer
            question_type = QuestionType.SHORT_ANSWER
        
        try:
            question = Question(
                id=question_id,
                text=question_text,
                question_type=question_type,
                choices=choices
            )
            
            return question, lines_consumed
            
        except ValueError as e:
            raise ParseError(f"Invalid question data: {e}", line_number=1)

    def clear_questions(self) -> None:
        """Reset the parser state."""
        self.current_question_id = 0
        self.logger.debug("Parser state cleared")