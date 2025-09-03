"""
converter.py: This module defines the TxtToQtiConverter class, which handles the conversion of text-based question banks to QTI packages.

The TxtToQtiConverter class provides methods to read text files containing questions, parse them, and generate QTI-compliant packages.

Main Features:
- Read and parse text files
- Generate QTI packages from parsed questions
- Handle exceptions during conversion

Example Usage:
    >>> from txttoqti.converter import TxtToQtiConverter
    >>> converter = TxtToQtiConverter()
    >>> qti_file = converter.convert_file("questions.txt")
    >>> print(f"QTI package created: {qti_file}")
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
import tempfile
import zipfile

from .parser import QuestionParser
from .qti_generator import QTIGenerator
from .validator import QuestionValidator
from .exceptions import ConversionError, FileError
from .logging_config import get_logger


class TxtToQtiConverter:
    """
    Main converter class that orchestrates the conversion process.
    
    Handles the full pipeline from text input to QTI package output.
    """
    
    def __init__(self) -> None:
        """Initialize the converter with required components."""
        self.logger = get_logger(__name__)
        self.parser = QuestionParser()
        self.qti_generator = QTIGenerator()
        self.validator = QuestionValidator()
        
        self.logger.info("TxtToQtiConverter initialized")

    def convert_file(
        self, 
        txt_file: str, 
        output_file: Optional[str] = None, 
        **kwargs: Any
    ) -> str:
        """
        Convert a text file containing questions to a QTI package.

        Args:
            txt_file: Path to the input text file containing questions
            output_file: Path for the output QTI ZIP file
            **kwargs: Additional options for conversion

        Returns:
            Path to the created QTI ZIP file

        Raises:
            FileError: If input file cannot be read
            ConversionError: If conversion process fails
        """
        try:
            self.logger.info(f"Starting conversion of {txt_file}")
            
            # Validate input file
            input_path = Path(txt_file)
            if not input_path.exists():
                raise FileError(f"Input file not found: {txt_file}", txt_file, "read")
            
            # Read file content
            try:
                with open(input_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                raise FileError(f"Cannot read file {txt_file}: {e}", txt_file, "read")
            
            # Check if file is empty
            if not content.strip():
                self.logger.warning(f"Input file {txt_file} is empty")
                return None
            
            # Parse questions
            questions = self.parser.parse(content)
            
            if not questions:
                self.logger.warning("No questions found in input file")
                return None
            
            # Validate questions
            for question in questions:
                self.validator.validate(question)
            
            # Generate QTI
            qti_xml = self.qti_generator.generate(questions)
            
            # Create output ZIP file
            if output_file is None:
                output_file = input_path.with_suffix('.qti').name
            
            output_path = Path(output_file)
            self._create_qti_package(qti_xml, output_path)
            
            self.logger.info(f"Successfully created QTI package: {output_path}")
            return str(output_path)
            
        except (FileError, ConversionError):
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during conversion: {e}")
            raise ConversionError(f"Conversion failed: {e}", original_error=e)

    def _create_qti_package(self, qti_xml: str, output_path: Path) -> None:
        """
        Create a QTI package ZIP file.
        
        Args:
            qti_xml: Generated QTI XML content
            output_path: Path for output ZIP file
        """
        try:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Add manifest
                manifest = self._generate_manifest()
                zf.writestr('imsmanifest.xml', manifest)
                
                # Add QTI XML
                zf.writestr('assessment.xml', qti_xml)
                
            self.logger.debug(f"QTI package created: {output_path}")
            
        except Exception as e:
            raise ConversionError(f"Failed to create QTI package: {e}", "package_creation", e)
    
    def _generate_manifest(self) -> str:
        """
        Generate IMS manifest XML for the QTI package.
        
        Returns:
            Manifest XML content
        """
        return '''<?xml version="1.0" encoding="UTF-8"?>
<manifest xmlns="http://www.imsglobal.org/xsd/imscp_v1p1" 
          xmlns:imsqti="http://www.imsglobal.org/xsd/imsqti_v2p1">
    <metadata>
        <schema>IMS QTI</schema>
        <schemaversion>2.1</schemaversion>
    </metadata>
    <organizations/>
    <resources>
        <resource identifier="assessment" type="imsqti_assessment_xmlv2p1" href="assessment.xml">
            <file href="assessment.xml"/>
        </resource>
    </resources>
</manifest>'''