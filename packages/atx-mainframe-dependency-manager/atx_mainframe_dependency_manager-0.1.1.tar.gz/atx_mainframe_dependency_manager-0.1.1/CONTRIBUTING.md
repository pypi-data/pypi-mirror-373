# Contributing to ATX Mainframe Dependency Manager

Thank you for your interest in contributing to ATX Mainframe Dependency Manager! This document provides guidelines for contributing to the project.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/arunkumars-mf/atx-mainframe-dependency-manager.git
   cd atx-mainframe-dependency-manager
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install in development mode:
   ```bash
   pip install -e .
   ```

## Running Tests

```bash
python -m pytest tests/
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to public functions and classes
- Keep functions focused and small

## Submitting Changes

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Reporting Issues

Please use the GitHub issue tracker to report bugs or request features. Include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details
