# xSystem Test Suite

## Overview

The xSystem test suite is organized into three main categories:

- **Core Tests**: Basic functionality and integration tests
- **Unit Tests**: Individual component tests organized by module
- **Integration Tests**: Cross-module interaction tests

## Test Structure

```
tests/
├── runner.py                    # Main test runner
├── core/                        # Core functionality tests
│   ├── runner.py               # Core test runner
│   ├── test_core.py            # Core utility tests
│   └── conftest.py             # Core test fixtures
├── unit/                        # Unit tests by module
│   ├── runner.py               # Unit test runner
│   ├── config_tests/           # Configuration tests
│   ├── performance_tests/      # Performance tests
│   ├── security_tests/         # Security tests
│   ├── threading_tests/        # Threading tests
│   ├── io_tests/               # I/O tests
│   ├── structures_tests/       # Data structure tests
│   └── patterns_tests/         # Design pattern tests
└── integration/                 # Integration tests
    ├── runner.py               # Integration test runner
    └── test_module_interactions.py
```

## Running Tests

### Run All Tests
```bash
python tests/runner.py
```

### Run Specific Categories
```bash
# Run only core tests
python tests/runner.py core

# Run only unit tests
python tests/runner.py unit

# Run only integration tests
python tests/runner.py integration
```

### Run Specific Unit Test Categories
```bash
# Run specific unit test category
python tests/runner.py unit config_tests
python tests/runner.py unit performance_tests
python tests/runner.py unit security_tests
```

### Direct Runner Usage
```bash
# Run core tests directly
python tests/core/runner.py

# Run unit tests directly
python tests/unit/runner.py

# Run integration tests directly
python tests/integration/runner.py
```

## Test Markers

Tests are categorized using pytest markers:

- `@pytest.mark.xsystem_core`: Core functionality tests
- `@pytest.mark.xsystem_unit`: Unit tests for individual components
- `@pytest.mark.xsystem_integration`: Integration tests between components
- `@pytest.mark.xsystem_config`: Configuration and setup tests
- `@pytest.mark.xsystem_performance`: Performance and benchmarking tests
- `@pytest.mark.xsystem_security`: Security validation tests
- `@pytest.mark.xsystem_threading`: Threading and concurrency tests
- `@pytest.mark.xsystem_io`: I/O operations tests
- `@pytest.mark.xsystem_structures`: Data structure tests
- `@pytest.mark.xsystem_patterns`: Design pattern tests
- `@pytest.mark.xsystem_monitoring`: Monitoring and metrics tests

## Test Coverage

The test suite provides comprehensive coverage for:

### Core Tests
- ThreadSafeFactory functionality
- PathValidator security
- AtomicFileWriter operations
- CircularReferenceDetector
- GenericHandlerFactory

### Unit Tests
- Configuration management
- Performance monitoring
- Security validation
- Threading utilities
- I/O operations
- Data structures
- Design patterns

### Integration Tests
- Cross-module interactions
- Concurrent operations
- Error recovery scenarios
- Performance integration

## Adding New Tests

### For Core Tests
1. Add test file to `tests/core/`
2. Use `@pytest.mark.xsystem_core` marker
3. Import from `exonware.xsystem`

### For Unit Tests
1. Add test file to appropriate subdirectory in `tests/unit/`
2. Use `@pytest.mark.xsystem_unit` marker
3. Test specific module functionality

### For Integration Tests
1. Add test file to `tests/integration/`
2. Use `@pytest.mark.xsystem_integration` marker
3. Test interactions between multiple modules

## Test Fixtures

Common test fixtures are available in `conftest.py` files:

- `clean_env`: Clean environment for testing
- `temp_log_dir`: Temporary logging directory
- `performance_data`: Sample performance data
- `circular_data`: Sample data with circular references

## Continuous Integration

Tests are automatically run in CI/CD pipelines with:

- Coverage reporting
- Performance benchmarking
- Security validation
- Cross-platform compatibility

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Descriptive Names**: Use clear, descriptive test names
3. **Proper Markers**: Always use appropriate pytest markers
4. **Error Handling**: Test both success and failure scenarios
5. **Performance**: Include performance tests for critical paths
6. **Security**: Validate security constraints and edge cases
