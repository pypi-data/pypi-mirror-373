"""
test_integration.py: Integration tests for the txttoqti package.

This file contains integration tests to ensure that different components of the txttoqti package work together correctly.
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.txttoqti.converter import TxtToQtiConverter
from src.txttoqti.parser import QuestionParser
from src.txttoqti.qti_generator import QTIGenerator

class TestTxtToQtiIntegration(unittest.TestCase):
    
    def setUp(self):
        self.converter = TxtToQtiConverter()
        self.parser = QuestionParser()
        self.qti_generator = QTIGenerator()

    def test_conversion_integration(self):
        # Sample text input
        sample_text = "What is the capital of France?\nA) Paris\nB) London\nC) Berlin\nD) Madrid"
        
        # Parse the sample text
        questions = self.parser.parse(sample_text)
        
        # Generate QTI from parsed questions
        qti_output = self.qti_generator.generate(questions)
        
        # Convert to QTI package
        qti_package = self.converter.convert(qti_output)
        
        # Check if the QTI package is created successfully
        self.assertIsNotNone(qti_package)
        self.assertTrue(qti_package.endswith('.zip'))

if __name__ == '__main__':
    unittest.main()