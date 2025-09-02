# spoon_ec5fd18c

spoon_ec5fd18c is an experimental Python project exploring
modern Python development best practices and GitHub workflows.

## Installation

You can install spoon_ec5fd18c using pip:

```bash
pip install spoon-ec5fd18c
```

To install with a CLI tool:

```bash
pip install 'spoon-ec5fd18c[cli]'
```

## Usage

### Command Line Interface

The package provides a command-line interface. After installation, run:

```bash
spoon-ec5fd18c World
### Python API

Import and use the library functions in your Python code:

```python
from spoon_ec5fd18c import hello

print(hello("World"))
```

## Development

### Setting up Development Environment

1. Clone the repository
2. Install development dependencies:
   ```bash
   uv sync --all-extras
   ```

### Running Tests

Run linters with:

```bash
uv run ruff format --check
uv run ruff check
uv run mypy src/
```

Run tests with:

```bash
uv run pytest tests/
```

### Building the Package

Build the package distribution:

```bash
uv build
```

### Documentation

Build the documentation:

```bash
uv run pdoc -o docs -d google spoon_ec5fd18c
```

To serve documentation locally with live reloading:

```bash
uv run pdoc -d google spoon_ec5fd18c
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Pass all linters and tests
6. Submit a pull request

## License

This project is licensed under Apache-2.0 license.

## Support

If you encounter any issues or have questions, please open an issue on the GitHub repository.

## Versioning

This project uses semantic versioning.
