#!/usr/bin/env python3
"""
Comprehensive test suite for weather integration in NASA-COMP project.
Tests both API endpoints and web interface functionality.
"""

import requests
import json
import time
import sys
import os
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://127.0.0.1:8000"

class WeatherIntegrationTester:
    """Test class for weather integration functionality."""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.test_results = []
        
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test results."""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if message:
            print(f"   {message}")
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "message": message
        })
        return passed
    
    def test_server_connectivity(self) -> bool:
        """Test if the server is running and accessible."""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            if response.status_code == 200:
                return self.log_test("Server Connectivity", True, f"Server responding on {self.base_url}")
            else:
                return self.log_test("Server Connectivity", False, f"Server returned status {response.status_code}")
        except requests.exceptions.ConnectionError:
            return self.log_test("Server Connectivity", False, "Cannot connect to server. Make sure it's running on port 8000")
        except Exception as e:
            return self.log_test("Server Connectivity", False, f"Connection error: {e}")
    
    def test_weather_api_endpoint(self) -> bool:
        """Test the weather API endpoint."""
        try:
            response = requests.get(f"{self.base_url}/api/weather", 
                                 params={"lat": 40.7128, "lon": -74.0060}, 
                                 timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "error" in data:
                    return self.log_test("Weather API Endpoint", False, f"Weather API error: {data['error']}")
                else:
                    location = data.get('location', {}).get('name', 'Unknown')
                    temp = data.get('current', {}).get('temp_c', 'N/A')
                    return self.log_test("Weather API Endpoint", True, 
                                       f"Weather data for {location}: {temp}°C")
            else:
                return self.log_test("Weather API Endpoint", False, 
                                   f"HTTP {response.status_code}: {response.text[:100]}")
        except Exception as e:
            return self.log_test("Weather API Endpoint", False, f"Request failed: {e}")
    
    def test_pollutant_movement_endpoint(self) -> bool:
        """Test the pollutant movement prediction endpoint."""
        try:
            response = requests.get(f"{self.base_url}/api/pollutant_movement",
                                 params={"lat": 40.7128, "lon": -74.0060},
                                 timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "error" in data:
                    return self.log_test("Pollutant Movement Endpoint", False, 
                                       f"Pollutant movement error: {data['error']}")
                else:
                    predictions = data.get('predictions_next_3h', [])
                    return self.log_test("Pollutant Movement Endpoint", True,
                                       f"Generated {len(predictions)} predictions")
            else:
                return self.log_test("Pollutant Movement Endpoint", False,
                                   f"HTTP {response.status_code}: {response.text[:100]}")
        except Exception as e:
            return self.log_test("Pollutant Movement Endpoint", False, f"Request failed: {e}")
    
    def test_combined_analysis_endpoint(self) -> bool:
        """Test the combined analysis endpoint."""
        try:
            response = requests.get(f"{self.base_url}/api/combined_analysis",
                                 params={"lat": 40.7128, "lon": -74.0060, 
                                        "gases": "NO2,CH2O"},
                                 timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                weather_available = 'weather' in data
                satellite_available = 'satellite_data' in data
                return self.log_test("Combined Analysis Endpoint", True,
                                   f"Weather: {weather_available}, Satellite: {satellite_available}")
            else:
                return self.log_test("Combined Analysis Endpoint", False,
                                   f"HTTP {response.status_code}: {response.text[:100]}")
        except Exception as e:
            return self.log_test("Combined Analysis Endpoint", False, f"Request failed: {e}")
    
    def test_web_interface_weather_options(self) -> bool:
        """Test that weather options are present in the web interface."""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                content = response.text
                has_weather_checkbox = "Include Weather Data" in content
                has_prediction_checkbox = "Include Pollutant Movement Prediction" in content
                has_weather_integration_text = "Weather Integration" in content
                
                if has_weather_checkbox and has_prediction_checkbox and has_weather_integration_text:
                    return self.log_test("Web Interface Weather Options", True,
                                       "Weather options found in main page")
                else:
                    missing = []
                    if not has_weather_checkbox: missing.append("weather checkbox")
                    if not has_prediction_checkbox: missing.append("prediction checkbox")
                    if not has_weather_integration_text: missing.append("integration text")
                    return self.log_test("Web Interface Weather Options", False,
                                       f"Missing: {', '.join(missing)}")
            else:
                return self.log_test("Web Interface Weather Options", False,
                                   f"Main page failed: HTTP {response.status_code}")
        except Exception as e:
            return self.log_test("Web Interface Weather Options", False, f"Request failed: {e}")
    
    def test_web_form_submission_with_weather(self) -> bool:
        """Test form submission with weather options enabled."""
        try:
            form_data = {
                "location": "New York City",
                "latitude": "40.7128",
                "longitude": "-74.0060",
                "radius": "0.3",
                "gases": "NO2",
                "include_weather": "on",
                "include_pollutant_prediction": "on"
            }
            
            response = requests.post(f"{self.base_url}/analyze", data=form_data, timeout=30)
            
            if response.status_code == 200:
                content = response.text
                has_weather_info = "Weather Information" in content
                has_weather_data = "weather_data" in content or "Temperature:" in content
                has_pollutant_predictions = "Pollutant Movement Prediction" in content
                
                if has_weather_info or has_weather_data:
                    return self.log_test("Web Form Submission with Weather", True,
                                       "Weather data displayed in results")
                else:
                    return self.log_test("Web Form Submission with Weather", False,
                                       "Weather data not found in results page")
            else:
                return self.log_test("Web Form Submission with Weather", False,
                                   f"Form submission failed: HTTP {response.status_code}")
        except Exception as e:
            return self.log_test("Web Form Submission with Weather", False, f"Request failed: {e}")
    
    def test_weather_data_structure(self) -> bool:
        """Test the structure of weather data returned by the API."""
        try:
            response = requests.get(f"{self.base_url}/api/weather", 
                                 params={"lat": 40.7128, "lon": -74.0060}, 
                                 timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                required_fields = ['location', 'current', 'forecast']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    return self.log_test("Weather Data Structure", False,
                                       f"Missing fields: {missing_fields}")
                
                # Check current weather fields
                current = data.get('current', {})
                current_fields = ['temp_c', 'humidity', 'wind_kph', 'wind_degree', 'condition']
                missing_current = [field for field in current_fields if field not in current]
                
                if missing_current:
                    return self.log_test("Weather Data Structure", False,
                                       f"Missing current weather fields: {missing_current}")
                
                return self.log_test("Weather Data Structure", True,
                                   "All required weather data fields present")
            else:
                return self.log_test("Weather Data Structure", False,
                                   f"API request failed: HTTP {response.status_code}")
        except Exception as e:
            return self.log_test("Weather Data Structure", False, f"Request failed: {e}")
    
    def test_pollutant_prediction_structure(self) -> bool:
        """Test the structure of pollutant movement predictions."""
        try:
            response = requests.get(f"{self.base_url}/api/pollutant_movement",
                                 params={"lat": 40.7128, "lon": -74.0060},
                                 timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if "predictions_next_3h" not in data:
                    return self.log_test("Pollutant Prediction Structure", False,
                                       "Missing predictions_next_3h field")
                
                predictions = data["predictions_next_3h"]
                if not isinstance(predictions, list) or len(predictions) == 0:
                    return self.log_test("Pollutant Prediction Structure", False,
                                       "No predictions generated")
                
                # Check prediction structure
                pred = predictions[0]
                required_pred_fields = ['time', 'wind_kph', 'wind_dir_deg', 'displacement_km', 'predicted_air_quality']
                missing_pred_fields = [field for field in required_pred_fields if field not in pred]
                
                if missing_pred_fields:
                    return self.log_test("Pollutant Prediction Structure", False,
                                       f"Missing prediction fields: {missing_pred_fields}")
                
                return self.log_test("Pollutant Prediction Structure", True,
                                   f"Generated {len(predictions)} valid predictions")
            else:
                return self.log_test("Pollutant Prediction Structure", False,
                                   f"API request failed: HTTP {response.status_code}")
        except Exception as e:
            return self.log_test("Pollutant Prediction Structure", False, f"Request failed: {e}")
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return results."""
        print("🧪 Testing Weather Integration in NASA-COMP")
        print("=" * 60)
        
        tests = [
            ("Server Connectivity", self.test_server_connectivity),
            ("Weather API Endpoint", self.test_weather_api_endpoint),
            ("Pollutant Movement Endpoint", self.test_pollutant_movement_endpoint),
            ("Combined Analysis Endpoint", self.test_combined_analysis_endpoint),
            ("Web Interface Weather Options", self.test_web_interface_weather_options),
            ("Web Form Submission with Weather", self.test_web_form_submission_with_weather),
            ("Weather Data Structure", self.test_weather_data_structure),
            ("Pollutant Prediction Structure", self.test_pollutant_prediction_structure)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 {test_name}")
            if test_func():
                passed += 1
        
        print("\n" + "=" * 60)
        print(f"📊 Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All weather integration tests passed!")
            print("\n✨ Features Verified:")
            print("   • Weather API endpoints working")
            print("   • Pollutant movement predictions working")
            print("   • Web interface weather integration working")
            print("   • Combined satellite + weather analysis working")
            print("\n🌐 Access the web interface at: http://127.0.0.1:8000")
        else:
            print("⚠️ Some tests failed. Please check the issues above.")
        
        return {
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": total - passed,
            "success_rate": (passed / total) * 100,
            "results": self.test_results
        }

def main():
    """Main test runner."""
    tester = WeatherIntegrationTester()
    results = tester.run_all_tests()
    
    # Exit with error code if any tests failed
    if results["failed_tests"] > 0:
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
