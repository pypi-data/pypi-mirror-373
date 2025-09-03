"""
cli: Command-line interface for the txttoqti package

This module provides a command-line interface for the txttoqti package, allowing users to convert text-based question banks to QTI packages directly from the terminal.

Usage:
    $ python -m txttoqti.cli [options]

Options:
    -h, --help          Show this help message and exit
    -i, --input FILE    Path to the input text file containing questions
    -o, --output FILE   Path for the output QTI ZIP file
    -v, --version       Show the version of the txttoqti package

Example:
    $ python -m txttoqti.cli -i questions.txt -o output.qti
"""

import argparse
from .converter import TxtToQtiConverter

def main():
    parser = argparse.ArgumentParser(description="Convert text-based question banks to QTI packages.")
    parser.add_argument('-i', '--input', required=True, help='Path to the input text file containing questions')
    parser.add_argument('-o', '--output', help='Path for the output QTI ZIP file')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0.0')

    args = parser.parse_args()

    converter = TxtToQtiConverter()
    qti_file = converter.convert_file(args.input, args.output)
    print(f"QTI package created: {qti_file}")

if __name__ == "__main__":
    main()