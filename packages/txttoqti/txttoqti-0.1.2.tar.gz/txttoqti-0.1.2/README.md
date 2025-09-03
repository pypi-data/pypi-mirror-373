# txttoqti

txttoqti is a universal converter that transforms text-based question banks into QTI (Question & Test Interoperability) packages compatible with Canvas LMS and other learning management systems. This package is designed to simplify the process of creating QTI packages from plain text files, making it easier for educators and developers to manage and distribute assessments.

## Features

- Convert plain text to QTI packages
- Compatibility with Canvas LMS
- Smart conversion with change detection
- Comprehensive validation of question formats
- No external dependencies (uses only Python standard library)

## Installation

To install the txttoqti package, you can use pip. Clone the repository and run the following command:

```
pip install .
```

Alternatively, you can install it directly from PyPI (if available):

```
pip install txttoqti
```

## Usage

Here is a basic example of how to use the txttoqti package:

```python
from txttoqti import TxtToQtiConverter

converter = TxtToQtiConverter()
qti_file = converter.convert_file("questions.txt")
print(f"QTI package created: {qti_file}")
```

## Documentation

For detailed documentation, including API references and examples, please refer to the `docs` directory.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.