# NASA-COMP Weather Integration Tests

This directory contains comprehensive tests for the weather integration functionality in the NASA-COMP project.

## Test Files

- `test_weather_integration.py` - Basic weather integration tests
- `test_city_weather_integration.py` - City-based weather integration tests
- `test_groq_integration.py` - GROQ AI integration tests
- `test_config.py` - Test configuration and constants
- `run_tests.py` - Comprehensive test runner script
- `__init__.py` - Package initialization file

## Running Tests

### Prerequisites

1. **Start the NASA-COMP server:**

   ```bash
   cd /path/to/NASA-COMP
   uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Ensure you have the required dependencies:**
   ```bash
   pip install requests
   ```

### Running the Tests

**Option 1: Run the test runner (recommended)**

```bash
cd tests
python run_tests.py
```

**Option 2: Run the main test script directly**

```bash
cd tests
python test_weather_integration.py
```

**Option 3: Run from project root**

```bash
python tests/test_weather_integration.py
```

## Test Coverage

The test suite covers the following areas:

### Basic Weather Integration

- ✅ Weather API endpoint (`/api/weather`)
- ✅ Pollutant movement prediction endpoint (`/api/pollutant_movement`)
- ✅ Combined analysis endpoint (`/api/combined_analysis`)
- ✅ Weather options in main page
- ✅ Form submission with weather data
- ✅ Weather data display in results page
- ✅ Weather data structure validation
- ✅ Pollutant prediction structure validation

### City-Based Weather Integration

- ✅ City name geocoding to coordinates
- ✅ Weather data retrieval for cities
- ✅ Pollutant movement prediction for cities
- ✅ User-friendly data display with clean, minimalistic design
- ✅ Direct API integration with city coordinates
- ✅ Multi-city testing (New York, London, Tokyo, Paris, Sydney)

### GROQ AI Integration

- ✅ GROQ API connectivity and authentication
- ✅ AI-powered weather interpretations
- ✅ Air quality and commute optimization advice
- ✅ Pollutant movement prediction insights
- ✅ Health recommendations for sensitive groups
- ✅ End-to-end AI integration with web interface

## Test Results

The tests will output:

- ✅ **PASS** - Test passed successfully
- ❌ **FAIL** - Test failed with error details

### Sample Output

```
🧪 Testing Weather Integration in NASA-COMP
============================================================

🔍 Server Connectivity
✅ PASS Server Connectivity
   Server responding on http://127.0.0.1:8000

🔍 Weather API Endpoint
✅ PASS Weather API Endpoint
   Weather data for New York: 18.3°C

📊 Results: 8/8 tests passed
🎉 All weather integration tests passed!
```

## Troubleshooting

### Common Issues

1. **"Cannot connect to server"**

   - Make sure the server is running on port 8000
   - Check that no firewall is blocking the connection

2. **"Weather API error"**

   - Ensure `WEATHER_API_KEY` is set in your `.env` file
   - Check that the API key is valid and has sufficient quota

3. **"Form submission failed"**
   - Verify that the server is running and accessible
   - Check that all required dependencies are installed

### Debug Mode

For detailed debugging, you can modify the test script to print more information:

```python
# Add this to see detailed responses
print(f"Response status: {response.status_code}")
print(f"Response content: {response.text[:200]}...")
```

## Adding New Tests

To add new tests:

1. Add a new test method to the `WeatherIntegrationTester` class
2. Follow the naming convention: `test_<feature_name>`
3. Use `self.log_test()` to log results
4. Add the test to the `run_all_tests()` method

Example:

```python
def test_new_feature(self) -> bool:
    """Test description."""
    try:
        # Test implementation
        return self.log_test("New Feature", True, "Success message")
    except Exception as e:
        return self.log_test("New Feature", False, f"Error: {e}")
```
