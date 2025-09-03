# Example usage of the txttoqti package

This document provides examples of how to use the `txttoqti` package for converting text-based question banks into QTI packages compatible with Canvas LMS and other learning management systems.

## Basic Usage

To get started with the `txttoqti` package, you can use the following example:

```python
from txttoqti import TxtToQtiConverter

# Create an instance of the converter
converter = TxtToQtiConverter()

# Convert a text file containing questions to a QTI package
qti_file = converter.convert_file("examples/sample_questions.txt")

print(f"QTI package created: {qti_file}")
```

## Command-Line Interface

You can also use the command-line interface to convert text files. Here is an example command:

```bash
python -m txttoqti.cli --input examples/sample_questions.txt --output output_package.zip
```

This command will read the questions from `sample_questions.txt` and create a QTI package named `output_package.zip`.

## Advanced Conversion

For advanced conversion features, you can use the `SmartConverter` class:

```python
from txttoqti import SmartConverter

# Create an instance of the smart converter
smart_converter = SmartConverter()

# Convert a text file with change detection
qti_file = smart_converter.convert_file("examples/sample_questions.txt")

print(f"Smart QTI package created: {qti_file}")
```

## Validation

Before converting, you may want to validate your text file to ensure it meets the required format:

```python
from txttoqti import QuestionValidator

# Create an instance of the validator
validator = QuestionValidator()

# Validate the text file
is_valid = validator.validate("examples/sample_questions.txt")

if is_valid:
    print("The questions file is valid.")
else:
    print("The questions file is invalid.")
```

These examples should help you get started with using the `txttoqti` package effectively. For more detailed information, please refer to the API documentation in `docs/api.md`.