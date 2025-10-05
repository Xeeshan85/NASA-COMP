"""
Test configuration for NASA-COMP weather integration tests.
"""

# Test server configuration
TEST_SERVER_URL = "http://127.0.0.1:8000"
TEST_TIMEOUT = 30

# Test coordinates (New York City)
TEST_LATITUDE = 40.7128
TEST_LONGITUDE = -74.0060

# Test location
TEST_LOCATION = "New York City"

# Test parameters
TEST_RADIUS = 0.3
TEST_GASES = "NO2,CH2O"

# Expected test data structure
EXPECTED_WEATHER_FIELDS = [
    'location', 'current', 'forecast'
]

EXPECTED_CURRENT_WEATHER_FIELDS = [
    'temp_c', 'humidity', 'wind_kph', 'wind_degree', 'condition'
]

EXPECTED_PREDICTION_FIELDS = [
    'time', 'wind_kph', 'wind_dir_deg', 'displacement_km', 'predicted_air_quality'
]

# Test thresholds
MIN_PREDICTIONS = 1
MAX_PREDICTIONS = 5
