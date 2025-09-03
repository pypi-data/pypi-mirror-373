"""
basic_usage.py: Demonstration of basic usage of the txttoqti package

This script provides a simple example of how to use the TxtToQtiConverter
to convert a text-based question bank into a QTI package.

Example Usage:
    1. Ensure you have a text file with questions (e.g., sample_questions.txt).
    2. Run this script to convert the text file to a QTI package.

"""

from src.txttoqti import convert_txt_to_qti

def main():
    # Path to the input text file containing questions
    txt_file = "examples/sample_questions.txt"
    
    # Optional: Specify the output QTI file name
    output_file = "output_package.zip"
    
    # Convert the text file to QTI package
    qti_file = convert_txt_to_qti(txt_file, output_file)
    
    print(f"QTI package created: {qti_file}")

if __name__ == "__main__":
    main()
"""