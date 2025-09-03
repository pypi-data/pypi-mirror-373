# API Documentation for txttoqti

## Overview

The `txttoqti` package provides a simple and efficient way to convert text-based question banks into QTI (Question & Test Interoperability) packages compatible with Canvas LMS and other learning management systems. This document outlines the main classes, methods, and usage examples for the API.

## Main Classes

### TxtToQtiConverter

The `TxtToQtiConverter` class is the primary interface for converting text files to QTI packages.

#### Methods

- `convert_file(txt_file, output_file=None, **kwargs)`

  Converts a specified text file into a QTI package.

  **Parameters:**
  - `txt_file` (str): Path to the input text file.
  - `output_file` (str, optional): Path for the output QTI ZIP file.
  - `**kwargs`: Additional options for conversion.

  **Returns:**
  - str: Path to the created QTI ZIP file.

### QuestionParser

The `QuestionParser` class is responsible for parsing text files and extracting questions.

#### Methods

- `parse(txt_file)`

  Parses the specified text file and returns a list of questions.

  **Parameters:**
  - `txt_file` (str): Path to the input text file.

  **Returns:**
  - list: A list of parsed questions.

### QTIGenerator

The `QTIGenerator` class generates QTI-compliant XML from parsed questions.

#### Methods

- `generate(questions)`

  Generates a QTI XML string from a list of questions.

  **Parameters:**
  - `questions` (list): A list of questions to be converted.

  **Returns:**
  - str: A QTI-compliant XML string.

### QuestionValidator

The `QuestionValidator` class validates the structure and content of questions before conversion.

#### Methods

- `validate(question)`

  Validates a single question.

  **Parameters:**
  - `question`: The question object to validate.

  **Returns:**
  - bool: True if valid, False otherwise.

## Exceptions

The package defines several custom exceptions for error handling:

- `TxtToQtiError`: General error for the txttoqti package.
- `ParseError`: Raised when there is an error in parsing the text file.
- `ValidationError`: Raised when validation of a question fails.
- `ConversionError`: Raised when there is an error during conversion.

## Usage Example

```python
from txttoqti import TxtToQtiConverter

converter = TxtToQtiConverter()
qti_file = converter.convert_file("questions.txt")
print(f"QTI package created: {qti_file}")
```

## Conclusion

The `txttoqti` package provides a robust solution for converting text-based question banks into QTI packages. For more detailed usage examples and installation instructions, please refer to the other documentation files in the `docs` directory.