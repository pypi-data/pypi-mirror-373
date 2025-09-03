# d-vecDB Python Client Tests

This directory contains comprehensive tests for the d-vecDB Python client library.

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── test_sync_client.py      # Synchronous client tests
├── test_async_client.py     # Asynchronous client tests
├── test_types.py           # Type validation and data model tests
├── test_performance.py     # Performance and benchmark tests
├── test_integration.py     # Integration and workflow tests
└── README.md              # This file
```

## Test Categories

### Unit Tests
- **test_sync_client.py**: Tests for synchronous client functionality
  - Client initialization and configuration
  - Collection management (CRUD operations)
  - Vector operations (insert, get, update, delete, search)
  - Server operations and health checks
  - Error handling and edge cases

- **test_async_client.py**: Tests for asynchronous client functionality
  - Async context managers and connection handling
  - Concurrent operations and batch processing
  - Async error handling and timeouts
  - Performance comparisons with sync client

- **test_types.py**: Tests for type definitions and validation
  - Pydantic model validation
  - Data type conversions (NumPy integration)
  - Serialization and deserialization
  - Input validation and error cases

### Integration Tests
- **test_integration.py**: Real-world workflow tests
  - Document embedding and semantic search
  - Recommendation system workflows
  - Content moderation pipelines
  - Data persistence and consistency
  - Error recovery scenarios

### Performance Tests
- **test_performance.py**: Performance and scalability tests
  - Insertion throughput benchmarks
  - Search performance under load
  - Memory usage analysis
  - Scalability with vector count and dimensions
  - Async vs sync performance comparison

## Running Tests

### Prerequisites
1. **d-vecDB Server**: Tests require a running d-vecDB server
   ```bash
   # Start the server (from project root)
   cargo run --bin vectordb-server
   ```

2. **Dependencies**: Install test dependencies
   ```bash
   pip install -e .[dev]
   ```

### Basic Test Execution

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m performance   # Performance tests only

# Run specific test files
pytest tests/test_sync_client.py
pytest tests/test_async_client.py
```

### Test Configuration

Tests can be configured via environment variables:

```bash
# Server configuration
export VECTORDB_TEST_HOST=localhost
export VECTORDB_TEST_PORT=8080
export VECTORDB_TEST_GRPC_PORT=9090

# Run tests with custom configuration
pytest
```

### Verbose Output

```bash
# Detailed output
pytest -v

# Show print statements
pytest -s

# Show test duration
pytest --durations=10
```

### Performance Testing

```bash
# Run only performance tests
pytest -m performance -v

# Run performance tests with timing
pytest -m performance --durations=0
```

## Test Fixtures

The test suite provides several reusable fixtures defined in `conftest.py`:

### Client Fixtures
- `client`: Configured synchronous VectorDB client
- `async_client`: Configured asynchronous VectorDB client

### Data Fixtures  
- `sample_vectors`: Set of test vectors for basic operations
- `large_sample_vectors`: Larger dataset for performance tests
- `query_vector`: Normalized query vector for search tests
- `test_collection_config`: Standard collection configuration

### Collection Management
- `clean_collection`: Ensures clean test collection (sync)
- `async_clean_collection`: Ensures clean test collection (async)
- `setup_test_collection`: Pre-populated test collection

### Utility Functions
- `generate_random_vectors()`: Generate test vectors with specified parameters
- `assert_vectors_equal()`: Compare vectors with tolerance
- `assert_query_results_valid()`: Validate search results

## Test Markers

Tests are organized with markers for easy filtering:

- `@pytest.mark.integration`: Integration tests requiring server
- `@pytest.mark.performance`: Performance and benchmark tests
- `@pytest.mark.slow`: Tests that take significant time
- `@pytest.mark.asyncio`: Async tests (handled automatically)

## Coverage

To run tests with coverage reporting:

```bash
# Install coverage tools
pip install pytest-cov

# Run with coverage
pytest --cov=vectordb_client --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html
```

## Debugging Tests

### Debug Individual Tests
```bash
# Run single test with output
pytest tests/test_sync_client.py::TestClientInitialization::test_default_initialization -s -v

# Drop into debugger on failure
pytest --pdb

# Drop into debugger on first failure
pytest -x --pdb
```

### Server Connection Issues
If tests fail due to server connection:

1. Verify server is running: `curl http://localhost:8080/health`
2. Check server logs for errors
3. Try connecting with different host/port:
   ```bash
   VECTORDB_TEST_HOST=127.0.0.1 VECTORDB_TEST_PORT=8080 pytest
   ```

## Writing New Tests

### Test Naming Convention
- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

### Example Test Structure
```python
class TestNewFeature:
    """Test description for new feature."""
    
    def test_basic_functionality(self, client, clean_collection):
        """Test basic functionality."""
        # Setup
        collection_name = clean_collection
        
        # Test code
        result = client.some_operation(collection_name)
        
        # Assertions
        assert result.success
        assert result.data is not None
    
    @pytest.mark.asyncio
    async def test_async_functionality(self, async_client, async_clean_collection):
        """Test async functionality."""
        collection_name = async_clean_collection
        
        result = await async_client.some_async_operation(collection_name)
        
        assert result.success
```

### Performance Test Example
```python
@pytest.mark.performance
def test_operation_performance(self, client, clean_collection):
    """Test performance of specific operation."""
    import time
    
    # Setup
    collection_name = clean_collection
    client.create_collection_simple(collection_name, 128, "cosine")
    
    # Performance measurement
    start_time = time.time()
    
    for i in range(1000):
        client.some_operation()
    
    end_time = time.time()
    duration = end_time - start_time
    rate = 1000 / duration
    
    print(f"Operation rate: {rate:.0f} ops/second")
    
    # Performance assertion
    assert rate > 100, f"Too slow: {rate:.0f} ops/sec"
```

## Continuous Integration

Tests are designed to run in CI environments:

### GitHub Actions Example
```yaml
name: Test d-vecDB Python Client

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      vectordb:
        image: d-vecdb:latest
        ports:
          - 8080:8080
          - 9090:9090
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -e .[dev]
    
    - name: Run tests
      run: |
        pytest -m "not performance" --cov=vectordb_client
    
    - name: Run performance tests
      run: |
        pytest -m performance --tb=short
```

## Troubleshooting

### Common Issues

1. **Server not available**: 
   - Ensure d-vecDB server is running on expected port
   - Check firewall settings
   - Verify server health: `curl http://localhost:8080/health`

2. **Async test failures**:
   - Check event loop configuration
   - Verify async client connection handling
   - Look for resource cleanup issues

3. **Performance test variance**:
   - Run on dedicated hardware when possible
   - Account for system load in assertions
   - Use relative performance comparisons

4. **Memory issues with large tests**:
   - Reduce test dataset size
   - Ensure proper cleanup in fixtures
   - Monitor memory usage during tests

### Getting Help

- Check test output and logs carefully
- Review fixture setup and teardown
- Verify server configuration and logs
- Check for resource leaks or connection issues
- Review similar tests for patterns