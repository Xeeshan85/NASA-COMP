#!/usr/bin/env python3
"""
Test script to verify weather integration works with city/region name input.
Tests the complete end-to-end flow from city name to weather data display.
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

class CityWeatherIntegrationTester:
    """Test class for city-based weather integration functionality."""
    
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
    
    def test_city_geocoding(self) -> bool:
        """Test that city names are properly geocoded to coordinates."""
        test_cities = [
            "New York City",
            "London, UK", 
            "Tokyo, Japan",
            "Paris, France",
            "Sydney, Australia"
        ]
        
        passed_cities = 0
        
        for city in test_cities:
            try:
                # Test the geocoding by submitting a form with just the city name
                form_data = {
                    "location": city,
                    "latitude": "",
                    "longitude": "",
                    "radius": "0.3",
                    "gases": "NO2",
                    "include_weather": "on",
                    "include_pollutant_prediction": "on"
                }
                
                response = requests.post(f"{self.base_url}/analyze", data=form_data, timeout=30)
                
                if response.status_code == 200:
                    # Check if the response contains weather data (indicating successful geocoding)
                    if "Weather Information" in response.text or "weather_data" in response.text:
                        passed_cities += 1
                        print(f"   ✓ {city} geocoded successfully")
                    else:
                        print(f"   ✗ {city} geocoding failed - no weather data")
                else:
                    print(f"   ✗ {city} request failed: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ✗ {city} error: {e}")
        
        success_rate = (passed_cities / len(test_cities)) * 100
        return self.log_test("City Geocoding", success_rate >= 80, 
                           f"{passed_cities}/{len(test_cities)} cities geocoded successfully ({success_rate:.1f}%)")
    
    def test_weather_data_for_city(self) -> bool:
        """Test weather data retrieval for a specific city."""
        try:
            # Test with New York City
            form_data = {
                "location": "New York City",
                "latitude": "",
                "longitude": "",
                "radius": "0.3",
                "gases": "NO2",
                "include_weather": "on",
                "include_pollutant_prediction": "on"
            }
            
            response = requests.post(f"{self.base_url}/analyze", data=form_data, timeout=30)
            
            if response.status_code == 200:
                content = response.text
                
                # Check for weather data indicators
                weather_indicators = [
                    "Weather Information",
                    "Current Weather Conditions",
                    "Temperature:",
                    "Humidity:",
                    "Wind Speed:",
                    "Air Quality Index"
                ]
                
                found_indicators = [indicator for indicator in weather_indicators if indicator in content]
                
                if len(found_indicators) >= 3:
                    return self.log_test("Weather Data for City", True,
                                       f"Found {len(found_indicators)} weather indicators: {', '.join(found_indicators[:3])}")
                else:
                    return self.log_test("Weather Data for City", False,
                                       f"Only found {len(found_indicators)} weather indicators")
            else:
                return self.log_test("Weather Data for City", False,
                                   f"Request failed: HTTP {response.status_code}")
        except Exception as e:
            return self.log_test("Weather Data for City", False, f"Request failed: {e}")
    
    def test_pollutant_prediction_for_city(self) -> bool:
        """Test pollutant movement prediction for a specific city."""
        try:
            # Test with London
            form_data = {
                "location": "London, UK",
                "latitude": "",
                "longitude": "",
                "radius": "0.3",
                "gases": "NO2",
                "include_weather": "on",
                "include_pollutant_prediction": "on"
            }
            
            response = requests.post(f"{self.base_url}/analyze", data=form_data, timeout=30)
            
            if response.status_code == 200:
                content = response.text
                
                # Check for pollutant prediction indicators
                prediction_indicators = [
                    "Pollutant Movement Prediction",
                    "Next 3 Hours",
                    "Wind Speed",
                    "Wind Direction",
                    "Movement:",
                    "Predicted Air Quality"
                ]
                
                found_indicators = [indicator for indicator in prediction_indicators if indicator in content]
                
                if len(found_indicators) >= 4:
                    return self.log_test("Pollutant Prediction for City", True,
                                       f"Found {len(found_indicators)} prediction indicators")
                else:
                    return self.log_test("Pollutant Prediction for City", False,
                                       f"Only found {len(found_indicators)} prediction indicators")
            else:
                return self.log_test("Pollutant Prediction for City", False,
                                   f"Request failed: HTTP {response.status_code}")
        except Exception as e:
            return self.log_test("Pollutant Prediction for City", False, f"Request failed: {e}")
    
    def test_user_friendly_display(self) -> bool:
        """Test that the weather and prediction data is displayed in a user-friendly format."""
        try:
            form_data = {
                "location": "Tokyo, Japan",
                "latitude": "",
                "longitude": "",
                "radius": "0.3",
                "gases": "NO2",
                "include_weather": "on",
                "include_pollutant_prediction": "on"
            }
            
            response = requests.post(f"{self.base_url}/analyze", data=form_data, timeout=30)
            
            if response.status_code == 200:
                content = response.text
                
                # Check for user-friendly display elements
                user_friendly_elements = [
                    "🌤️",  # Weather emoji
                    "🌪️",  # Prediction emoji
                    "°C",   # Temperature units
                    "°F",   # Temperature units
                    "km/h", # Wind speed units
                    "mph",  # Wind speed units
                    "μg/m³", # Air quality units
                    "Interpretation:", # Help text
                    "Carbon Monoxide", # Full pollutant names
                    "Nitrogen Dioxide", # Full pollutant names
                ]
                
                found_elements = [element for element in user_friendly_elements if element in content]
                
                if len(found_elements) >= 6:
                    return self.log_test("User-Friendly Display", True,
                                       f"Found {len(found_elements)} user-friendly elements")
                else:
                    return self.log_test("User-Friendly Display", False,
                                       f"Only found {len(found_elements)} user-friendly elements")
            else:
                return self.log_test("User-Friendly Display", False,
                                   f"Request failed: HTTP {response.status_code}")
        except Exception as e:
            return self.log_test("User-Friendly Display", False, f"Request failed: {e}")
    
    def test_weather_api_direct_with_city(self) -> bool:
        """Test weather API directly with coordinates from a city."""
        try:
            # First get coordinates for a city by making a form request
            form_data = {
                "location": "Paris, France",
                "latitude": "",
                "longitude": "",
                "radius": "0.3",
                "gases": "NO2",
                "include_weather": "on",
                "include_pollutant_prediction": "on"
            }
            
            response = requests.post(f"{self.base_url}/analyze", data=form_data, timeout=30)
            
            if response.status_code == 200:
                # Extract coordinates from the response (they should be in the meta section)
                content = response.text
                
                # Look for coordinate pattern in the response
                import re
                coord_pattern = r'\(([0-9.-]+),\s*([0-9.-]+)\)'
                matches = re.findall(coord_pattern, content)
                
                if matches:
                    lat, lon = matches[0]
                    
                    # Now test the weather API directly with these coordinates
                    weather_response = requests.get(f"{self.base_url}/api/weather", 
                                                  params={"lat": lat, "lon": lon}, 
                                                  timeout=10)
                    
                    if weather_response.status_code == 200:
                        weather_data = weather_response.json()
                        if "error" not in weather_data and "current" in weather_data:
                            return self.log_test("Weather API Direct with City", True,
                                               f"Weather API working for Paris coordinates ({lat}, {lon})")
                        else:
                            return self.log_test("Weather API Direct with City", False,
                                               "Weather API returned error or missing data")
                    else:
                        return self.log_test("Weather API Direct with City", False,
                                           f"Weather API failed: HTTP {weather_response.status_code}")
                else:
                    return self.log_test("Weather API Direct with City", False,
                                       "Could not extract coordinates from city geocoding")
            else:
                return self.log_test("Weather API Direct with City", False,
                                   f"City geocoding failed: HTTP {response.status_code}")
        except Exception as e:
            return self.log_test("Weather API Direct with City", False, f"Request failed: {e}")
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all city-based weather integration tests."""
        print("🏙️ Testing City-Based Weather Integration in NASA-COMP")
        print("=" * 60)
        
        tests = [
            ("City Geocoding", self.test_city_geocoding),
            ("Weather Data for City", self.test_weather_data_for_city),
            ("Pollutant Prediction for City", self.test_pollutant_prediction_for_city),
            ("User-Friendly Display", self.test_user_friendly_display),
            ("Weather API Direct with City", self.test_weather_api_direct_with_city)
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
            print("🎉 All city-based weather integration tests passed!")
            print("\n✨ Features Verified:")
            print("   • City name geocoding to coordinates")
            print("   • Weather data retrieval for cities")
            print("   • Pollutant movement prediction for cities")
            print("   • User-friendly data display")
            print("   • Direct API integration with city coordinates")
            print("\n🌐 Users can now:")
            print("   • Enter any city name in the form")
            print("   • Get real-time weather data for that city")
            print("   • See pollutant movement predictions")
            print("   • View data in an easy-to-understand format")
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
    tester = CityWeatherIntegrationTester()
    results = tester.run_all_tests()
    
    # Exit with error code if any tests failed
    if results["failed_tests"] > 0:
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
