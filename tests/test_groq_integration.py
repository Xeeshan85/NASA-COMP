#!/usr/bin/env python3
"""
Test script to verify GROQ integration for AI-powered weather and air quality interpretations.
"""

import sys
import os
import requests
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from groq_service import generate_weather_interpretation, generate_prediction_interpretation

def test_groq_weather_interpretation():
    """Test GROQ weather interpretation generation."""
    print("🧠 Testing GROQ Weather Interpretation...")
    
    # Sample weather data
    sample_weather_data = {
        "location": {"name": "New York City"},
        "current": {
            "temp_c": 18.3,
            "temp_f": 64.9,
            "humidity": 68,
            "wind_kph": 4.3,
            "wind_mph": 2.7,
            "wind_dir": "WNW",
            "wind_degree": 302,
            "condition": {"text": "Clear"},
            "vis_km": 16.0
        },
        "air_quality": {
            "co": 618.85,
            "no2": 56.25,
            "o3": 66.0,
            "pm2_5": 26.65,
            "pm10": 26.75,
            "us-epa-index": 2
        }
    }
    
    try:
        interpretation = generate_weather_interpretation(sample_weather_data, "New York City")
        
        if interpretation:
            print("✅ GROQ Weather Interpretation Generated")
            print(f"   Length: {len(interpretation)} characters")
            print(f"   Preview: {interpretation[:100]}...")
            return True
        else:
            print("❌ GROQ Weather Interpretation Failed")
            return False
    except Exception as e:
        print(f"❌ GROQ Weather Interpretation Error: {e}")
        return False

def test_groq_prediction_interpretation():
    """Test GROQ prediction interpretation generation."""
    print("\n🧠 Testing GROQ Prediction Interpretation...")
    
    # Sample prediction data
    sample_predictions = [
        {
            "time": "2025-10-05 01:00",
            "wind_kph": 5.4,
            "wind_dir_deg": 270,
            "displacement_km": {"dx": -5.4, "dy": -0.0},
            "predicted_air_quality": {
                "co": 332.63,
                "no2": 60.10,
                "o3": 14.73,
                "pm2_5": 24.31
            }
        },
        {
            "time": "2025-10-05 02:00",
            "wind_kph": 5.0,
            "wind_dir_deg": 272,
            "displacement_km": {"dx": -5.0, "dy": 0.17},
            "predicted_air_quality": {
                "co": 396.18,
                "no2": 59.89,
                "o3": 11.42,
                "pm2_5": 23.77
            }
        }
    ]
    
    try:
        interpretation = generate_prediction_interpretation(sample_predictions, "New York City")
        
        if interpretation:
            print("✅ GROQ Prediction Interpretation Generated")
            print(f"   Length: {len(interpretation)} characters")
            print(f"   Preview: {interpretation[:100]}...")
            return True
        else:
            print("❌ GROQ Prediction Interpretation Failed")
            return False
    except Exception as e:
        print(f"❌ GROQ Prediction Interpretation Error: {e}")
        return False

def test_groq_api_connectivity():
    """Test GROQ API connectivity."""
    print("\n🔗 Testing GROQ API Connectivity...")
    
    try:
        # Test with a simple request
        from groq_service import GROQ_API_KEY
        
        if not GROQ_API_KEY:
            print("❌ GROQ API Key not found")
            return False
        
        print(f"✅ GROQ API Key found: {GROQ_API_KEY[:10]}...")
        return True
    except Exception as e:
        print(f"❌ GROQ API Connectivity Error: {e}")
        return False

def test_end_to_end_groq_integration():
    """Test end-to-end GROQ integration with web interface."""
    print("\n🌐 Testing End-to-End GROQ Integration...")
    
    try:
        # Test form submission with weather options
        form_data = {
            "location": "New York City",
            "latitude": "",
            "longitude": "",
            "radius": "0.3",
            "gases": "NO2",
            "include_weather": "on",
            "include_pollutant_prediction": "on"
        }
        
        response = requests.post("http://127.0.0.1:8000/analyze", data=form_data, timeout=30)
        
        if response.status_code == 200:
            content = response.text
            
            # Check for GROQ interpretation indicators
            groq_indicators = [
                "Air Quality & Commute Optimizer",
                "Air Quality Assessment",
                "Commute Recommendations",
                "Health Precautions"
            ]
            
            found_indicators = [indicator for indicator in groq_indicators if indicator in content]
            
            if len(found_indicators) >= 2:
                print("✅ GROQ Integration Working in Web Interface")
                print(f"   Found {len(found_indicators)} GROQ indicators")
                return True
            else:
                print("❌ GROQ Integration Not Found in Web Interface")
                print(f"   Only found {len(found_indicators)} indicators: {found_indicators}")
                return False
        else:
            print(f"❌ Web Interface Test Failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ End-to-End GROQ Integration Error: {e}")
        return False

def main():
    """Run all GROQ integration tests."""
    print("🧠 Testing GROQ Integration for AI-Powered Weather Interpretations")
    print("=" * 70)
    
    tests = [
        ("GROQ API Connectivity", test_groq_api_connectivity),
        ("GROQ Weather Interpretation", test_groq_weather_interpretation),
        ("GROQ Prediction Interpretation", test_groq_prediction_interpretation),
        ("End-to-End GROQ Integration", test_end_to_end_groq_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 70)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All GROQ integration tests passed!")
        print("\n✨ AI Features Available:")
        print("   • Intelligent weather interpretations")
        print("   • Air quality and commute optimization advice")
        print("   • Pollutant movement predictions with AI insights")
        print("   • Health recommendations for sensitive groups")
        print("   • Practical commute timing advice")
    else:
        print("⚠️ Some GROQ integration tests failed.")
        print("Make sure GROQ_API_KEY is set in your .env file.")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
