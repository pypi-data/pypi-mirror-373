"""
Exception classes for the txttoqti package.

Provides a hierarchy of custom exceptions for better error handling
and debugging throughout the conversion process.
"""

from typing import Optional, Any, Dict


class TxtToQtiError(Exception):
    """
    Base class for exceptions in the txttoqti package.
    
    Provides common functionality for all txttoqti exceptions including
    error codes and context information.
    """
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}
    
    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class ParseError(TxtToQtiError):
    """
    Exception raised for errors in parsing questions.
    
    Used when the input text format is invalid or cannot be processed.
    """
    
    def __init__(
        self, 
        message: str, 
        line_number: Optional[int] = None,
        line_content: Optional[str] = None
    ) -> None:
        context = {}
        if line_number is not None:
            context["line_number"] = line_number
        if line_content is not None:
            context["line_content"] = line_content
            
        super().__init__(message, "PARSE_ERROR", context)
        self.line_number = line_number
        self.line_content = line_content


class ValidationError(TxtToQtiError):
    """
    Exception raised for validation errors in questions.
    
    Used when parsed questions don't meet QTI or Canvas requirements.
    """
    
    def __init__(
        self, 
        message: str, 
        question_id: Optional[str] = None,
        validation_rule: Optional[str] = None
    ) -> None:
        context = {}
        if question_id is not None:
            context["question_id"] = question_id
        if validation_rule is not None:
            context["validation_rule"] = validation_rule
            
        super().__init__(message, "VALIDATION_ERROR", context)
        self.question_id = question_id
        self.validation_rule = validation_rule


class ConversionError(TxtToQtiError):
    """
    Exception raised for errors during conversion to QTI.
    
    Used when the conversion process fails due to technical issues.
    """
    
    def __init__(
        self, 
        message: str, 
        stage: Optional[str] = None,
        original_error: Optional[Exception] = None
    ) -> None:
        context = {}
        if stage is not None:
            context["stage"] = stage
        if original_error is not None:
            context["original_error"] = str(original_error)
            context["original_error_type"] = type(original_error).__name__
            
        super().__init__(message, "CONVERSION_ERROR", context)
        self.stage = stage
        self.original_error = original_error


class FileError(TxtToQtiError):
    """
    Exception raised for file-related errors.
    
    Used when input files cannot be read or output files cannot be written.
    """
    
    def __init__(
        self, 
        message: str, 
        file_path: Optional[str] = None,
        operation: Optional[str] = None
    ) -> None:
        context = {}
        if file_path is not None:
            context["file_path"] = file_path
        if operation is not None:
            context["operation"] = operation
            
        super().__init__(message, "FILE_ERROR", context)
        self.file_path = file_path
        self.operation = operation