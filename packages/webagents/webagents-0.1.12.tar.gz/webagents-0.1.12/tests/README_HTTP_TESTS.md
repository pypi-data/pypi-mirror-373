# HTTP Test Suite

Professional pytest test suite for the HTTP decorator and capabilities system.

## 📁 Test Structure

```
tests/
├── agents/core/
│   ├── test_base_agent_http.py                  # Original comprehensive HTTP tests
│   └── test_http_capabilities_integration.py    # New integration tests
├── server/
│   └── test_http_server_integration.py          # Server integration tests
└── run_http_tests.py                            # Simple test runner (non-pytest)
```

## 🧪 Test Files Overview

### `test_base_agent_http.py` (22 tests)
**Original comprehensive HTTP test suite**

- `TestHTTPDecorator` - Basic @http decorator functionality
- `TestBaseAgentHTTP` - BaseAgent HTTP handler integration  
- `TestCapabilitiesSystem` - Capabilities auto-registration
- `TestDirectRegistration` - @agent.http direct registration
- `TestHTTPIntegration` - Complex integration scenarios

### `test_http_capabilities_integration.py` (25+ tests)
**Comprehensive integration test suite**

- `TestHTTPDecorator` - Extended decorator testing
- `TestBaseAgentHTTPIntegration` - Agent integration testing
- `TestCapabilitiesAutoRegistration` - Auto-registration testing
- `TestDirectRegistration` - Direct registration methods
- `TestHTTPFunctionExecution` - Function execution testing
- `TestComplexIntegrationScenarios` - Real-world scenarios
- `TestHTTPCapabilitiesIntegration` - End-to-end integration

### `test_http_server_integration.py` (15+ tests)
**Server integration test suite**

- `TestHTTPHandlerBasics` - Basic handler functionality
- `TestServerIntegration` - FastAPI server integration
- `TestHTTPEndpointCalls` - Actual HTTP endpoint testing
- `TestDirectRegistration` - Direct registration with server
- `TestCapabilitiesAutoRegistration` - Auto-registration with server
- `TestHTTPIntegrationScenarios` - Complex server scenarios

### `run_http_tests.py`
**Simple test runner for verification**

Non-pytest runner that tests core functionality:
- HTTP decorator functionality
- BaseAgent integration
- Capabilities auto-registration
- Direct registration methods
- Scope filtering
- Conflict detection

## 🚀 Running Tests

### Full Test Suite
```bash
# Run all HTTP-related tests
python -m pytest tests/agents/core/test_base_agent_http.py -v
python -m pytest tests/agents/core/test_http_capabilities_integration.py -v
python -m pytest tests/server/test_http_server_integration.py -v

# Run all tests together
python -m pytest tests/agents/core/test_*http*.py tests/server/test_*http*.py -v
```

### Specific Test Classes
```bash
# Test just the HTTP decorator
python -m pytest tests/agents/core/test_http_capabilities_integration.py::TestHTTPDecorator -v

# Test BaseAgent integration
python -m pytest tests/agents/core/test_base_agent_http.py::TestBaseAgentHTTP -v

# Test server integration
python -m pytest tests/server/test_http_server_integration.py::TestServerIntegration -v
```

### Individual Tests
```bash
# Test specific functionality
python -m pytest tests/agents/core/test_base_agent_http.py::TestHTTPDecorator::test_http_decorator_basic -v

# Test conflict detection
python -m pytest tests/agents/core/test_http_capabilities_integration.py::TestBaseAgentHTTPIntegration::test_http_handler_conflict_detection -v
```

### Simple Verification
```bash
# If pytest hangs, use the simple runner
cd tests
python run_http_tests.py
```

## 📋 Test Coverage

### Core Functionality
- ✅ @http decorator with all parameters
- ✅ HTTP method validation (GET, POST, PUT, DELETE, etc.)
- ✅ Scope-based access control
- ✅ Subpath normalization
- ✅ Context injection
- ✅ Error handling and validation

### BaseAgent Integration
- ✅ HTTP handler registration via `__init__`
- ✅ HTTP handler conflict detection
- ✅ Core path conflict prevention
- ✅ Scope-based filtering
- ✅ Thread-safe registration
- ✅ Metadata preservation

### Capabilities System
- ✅ Auto-registration based on decorator types
- ✅ Mixed decorator support (@tool, @hook, @handoff, @http)
- ✅ Integration with explicit parameters
- ✅ Undecorated function handling
- ✅ Type detection and categorization

### Direct Registration
- ✅ @agent.http() FastAPI-style syntax
- ✅ @agent.tool() integration
- ✅ @agent.hook() and @agent.handoff() support
- ✅ Parameter support and scope handling
- ✅ Immediate registration
- ✅ Conflict detection

### Server Integration
- ✅ FastAPI route registration
- ✅ Route pattern (`/{agent_name}/{subpath}`)
- ✅ Request parameter handling
- ✅ Query parameters and JSON bodies
- ✅ Path parameters
- ✅ Error handling and HTTP status codes
- ✅ Multiple agent support

### Advanced Scenarios
- ✅ HTTP endpoints using agent tools
- ✅ Complex agent setups with all capability types
- ✅ Multiple agents with different scopes
- ✅ End-to-end integration flows
- ✅ Real-world usage patterns

## 🎯 Test Categories

### Unit Tests
Testing individual components in isolation:
- HTTP decorator functionality
- Function metadata and validation
- Scope filtering logic
- Conflict detection algorithms

### Integration Tests
Testing component interactions:
- HTTP handlers with BaseAgent
- Capabilities auto-registration
- Direct registration methods
- Agent-server integration

### System Tests
Testing complete workflows:
- End-to-end HTTP request handling
- Multiple agent deployments
- Complex integration scenarios
- Real-world usage patterns

## 🔧 Test Fixtures

### Reusable Fixtures
```python
@pytest.fixture
def weather_handler():
    """Weather API endpoint fixture"""
    @http("/weather", method="get", scope="owner")
    def get_weather(location: str, units: str = "celsius") -> dict:
        return {"location": location, "temperature": 25, "units": units}
    return get_weather

@pytest.fixture
def test_agent(weather_handler):
    """Test agent with HTTP handlers"""
    return BaseAgent(
        name="test-agent",
        capabilities=[weather_handler, ...]
    )

@pytest.fixture
def test_server(test_agent):
    """Test server with HTTP-enabled agent"""
    return RobutlerServer(agents=[test_agent])

@pytest.fixture
def test_client(test_server):
    """Test client for HTTP requests"""
    return TestClient(test_server.app)
```

## 📊 Test Results Expected

When all tests pass, you should see:

```
tests/agents/core/test_base_agent_http.py::TestHTTPDecorator::test_http_decorator_basic PASSED
tests/agents/core/test_base_agent_http.py::TestBaseAgentHTTP::test_http_handler_registration PASSED
tests/agents/core/test_base_agent_http.py::TestCapabilitiesSystem::test_capabilities_auto_registration PASSED
...

tests/agents/core/test_http_capabilities_integration.py::TestHTTPDecorator::test_http_decorator_basic PASSED
tests/agents/core/test_http_capabilities_integration.py::TestBaseAgentHTTPIntegration::test_http_handler_registration_via_init PASSED
...

tests/server/test_http_server_integration.py::TestHTTPHandlerBasics::test_agent_http_registration PASSED
tests/server/test_http_server_integration.py::TestServerIntegration::test_server_creation PASSED
...

========================= 60+ passed in X.XXs =========================
```

## 🐛 Troubleshooting

### Common Issues

1. **Tests hanging during execution**
   - Use the simple test runner: `cd tests && python run_http_tests.py`
   - Run individual test methods instead of full classes

2. **Import errors**
   - Ensure you're running from the project root
   - Check that all dependencies are installed

3. **Server integration tests failing**
   - Disable monitoring: `enable_monitoring=False`
   - Use `TestClient` instead of actual HTTP requests

### Debug Mode
```bash
# Run with verbose output and stop on first failure
python -m pytest tests/agents/core/test_base_agent_http.py -v -x

# Run with debug output
python -m pytest tests/agents/core/test_base_agent_http.py -v -s
```

## 🎉 Summary

This professional pytest test suite provides comprehensive coverage of the HTTP decorator and capabilities system. With 60+ tests across multiple files, it ensures the implementation is robust, reliable, and ready for production use.

**Key Features:**
- Professional pytest structure with proper naming
- Comprehensive test coverage of all functionality
- Proper test organization with classes and fixtures
- Integration tests with server components
- Reusable test fixtures and utilities
- Clear test documentation and examples 