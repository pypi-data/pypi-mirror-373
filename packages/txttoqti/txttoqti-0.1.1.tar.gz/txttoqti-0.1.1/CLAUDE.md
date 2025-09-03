# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

txttoqti is a Python package that converts text-based question banks into QTI (Question & Test Interoperability) packages compatible with Canvas LMS. The project uses only Python standard library dependencies and follows a modular architecture.

## Commands

### Development and Testing
- `python -m pytest tests/` - Run all unit tests
- `python -m unittest tests.test_core` - Run core functionality tests  
- `python -m unittest tests.test_integration` - Run integration tests
- `pip install -e .` - Install package in development mode
- `python main.py` - Run the basic entry point

### CLI Usage
- `python -m txttoqti.cli -i questions.txt -o output.qti` - Convert text file to QTI package
- `python -m txttoqti.cli --help` - Show CLI help

### Package Installation
- `pip install .` - Install the package from source

## Architecture

The codebase follows a clean separation of concerns with these core modules:

### Core Components (src/txttoqti/)
- **converter.py**: Main `TxtToQtiConverter` class that orchestrates the conversion process
- **parser.py**: `QuestionParser` handles text parsing and question extraction  
- **qti_generator.py**: `QTIGenerator` creates QTI-compliant XML and ZIP packages
- **validator.py**: `QuestionValidator` validates question formats and content
- **smart_converter.py**: `SmartConverter` provides change detection and incremental updates
- **cli.py**: Command-line interface with argparse integration

### Supporting Modules  
- **exceptions.py**: Custom exception classes (TxtToQtiError, ParseError, ValidationError, ConversionError)
- **utils.py**: Utility functions for text cleaning, file validation, and timestamps
- **__init__.py**: Package exports and convenience function `convert_txt_to_qti()`

### Question Format
Questions are parsed from text files using a structured format with numbered questions, multiple choice options (a, b, c, d), and correct answer indicators. See `examples/sample_questions.txt` for the expected format.

### Entry Points
- Programmatic: Import `TxtToQtiConverter` or use `convert_txt_to_qti()` function
- CLI: `python -m txttoqti.cli` with input/output arguments
- Basic: `main.py` provides simple "Hello from txttoqti!" entry point

### Testing Structure
- `tests/test_core.py`: Unit tests for core converter functionality
- `tests/test_integration.py`: Integration tests for end-to-end workflows
- Test files expect sample data in `tests/` directory

## Development Notes

The project is in active development with skeleton implementations. Most core classes have method signatures defined but require implementation. The package is designed to be lightweight with no external dependencies beyond Python standard library.