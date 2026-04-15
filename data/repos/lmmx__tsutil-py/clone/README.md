# Python Syntax Tree Printer

This project is a Python-based syntax tree printer utility that reads a source code file,
guesses the language based on the file extension, and prints the syntax tree using tree-sitter.

## Features

- Supports Rust and Python source files
- Prints detailed syntax tree nodes
- Uses Tree-sitter for parsing
- Syntax highlighting for parse trees
- Lists all node IDs and their corresponding names for a language
- Query the program's Concrete Syntax Tree (CST) using S-expressions

## Requirements

- Python 3.10+
- pip

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/python-syntax-tree-printer.git
   cd python-syntax-tree-printer
   ```

2. Install the required dependencies:
   ```
   pip install .
   ```

## Usage

1. Run the program with a file path as an argument to print the syntax tree:
   ```
   tsutil <file-path>
   ```

2. Run the program with the `--highlight` flag to print the syntax tree with syntax highlighting:
   ```
   tsutil <file-path> --highlight
   ```

3. Run the program with the `--list-ids` flag to list all node IDs and their corresponding names for the language:
   ```
   tsutil <file-path> --list-ids
   ```

4. Run the program with the `--query` flag to execute a query on the syntax tree:
   ```
   tsutil <file-path> --query "<query-string>"
   ```

## Example

To print the syntax tree of a Python source file:

```
tsutil example/simple_addition.py
```

To print the syntax tree with syntax highlighting:

```
tsutil example/simple_addition.py --highlight
```

To list all node IDs and their corresponding names for a Python source file:

```
tsutil example/simple_addition.py --list-ids
```

To query the syntax tree for function definitions:

```
tsutil example/simple_addition.py --query "(function_definition name: (_) @function_name)"
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Acknowledgements

- [Tree-sitter](https://tree-sitter.github.io/tree-sitter/) for the parsing library
- [py-tree-sitter](https://github.com/tree-sitter/py-tree-sitter) for the Python bindings
- [termcolor](https://pypi.org/project/termcolor/) for terminal colorization
