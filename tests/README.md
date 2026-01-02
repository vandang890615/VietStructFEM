# VietStruct FEM Tests

This directory contains unit tests and integration tests for the VietStruct FEM package.

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=steeldeckfem --cov-report=html

# Run specific test file
pytest tests/test_fem_analyzer.py

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_fem_analyzer.py::test_build_fem_model
```

## Test Structure

- `test_fem_analyzer.py` - Tests for FEM analysis module
- `test_floor_deck.py` - Tests for steel deck design
- `test_engineering.py` - Tests for industrial building features
- `test_stability.py` - Tests for stability analysis
- `test_wind_zones.py` - Tests for wind zone database
- `test_integration.py` - End-to-end integration tests
- `conftest.py` - Shared fixtures and configuration

## Coverage Target

Target: 70-80% code coverage

## Writing Tests

All tests should follow these conventions:
1. Use descriptive test names: `test_<function>_<scenario>_<expected_result>`
2. One assertion per test when possible
3. Use fixtures for common test data
4. Mock external dependencies (PyNite, file I/O, etc.)
5. Test both success and failure cases
