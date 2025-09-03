"""
txt-to-qti: Universal converter from text-based question banks to Canvas LMS QTI packages

This library provides a simple, robust way to convert plain text question banks
into QTI (Question & Test Interoperability) packages compatible with Canvas LMS
and other learning management systems.

Main Features:
- Convert plain text to QTI packages
- Canvas LMS compatibility 
- Smart conversion with change detection
- Comprehensive validation
- No external dependencies (uses only Python standard library)

Example Usage:
    >>> from txttoqti import TxtToQtiConverter
    >>> converter = TxtToQtiConverter()
    >>> qti_file = converter.convert_file("questions.txt")
    >>> print(f"QTI package created: {qti_file}")

Author: Educational Tools Team
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Educational Tools Team"
__license__ = "MIT"

# Main API exports
from .converter import TxtToQtiConverter
from .parser import QuestionParser
from .qti_generator import QTIGenerator
from .validator import QuestionValidator
from .smart_converter import SmartConverter

# Model exports
from .models import Question, QuestionType, Choice, Assessment

# Exception exports
from .exceptions import (
    TxtToQtiError,
    ParseError,
    ValidationError,
    ConversionError,
    FileError,
)

# Utility exports
from .utils import (
    clean_text,
    validate_file,
    get_file_timestamp,
)

__all__ = [
    # Main classes
    "TxtToQtiConverter",
    "QuestionParser", 
    "QTIGenerator",
    "QuestionValidator",
    "SmartConverter",
    
    # Models
    "Question",
    "QuestionType",
    "Choice",
    "Assessment",
    
    # Exceptions
    "TxtToQtiError",
    "ParseError",
    "ValidationError", 
    "ConversionError",
    "FileError",
    
    # Utilities
    "clean_text",
    "validate_file",
    "get_file_timestamp",
    
    # Package info
    "__version__",
    "__author__",
    "__license__",
]

# Module-level convenience function
def convert_txt_to_qti(txt_file, output_file=None, **kwargs):
    """
    Convenience function to convert a text file to QTI package.
    
    Args:
        txt_file (str): Path to input text file
        output_file (str, optional): Path for output QTI ZIP file
        **kwargs: Additional options for conversion
        
    Returns:
        str: Path to created QTI ZIP file
        
    Example:
        >>> qti_file = convert_txt_to_qti("my_questions.txt")
    """
    converter = TxtToQtiConverter()
    return converter.convert_file(txt_file, output_file, **kwargs)