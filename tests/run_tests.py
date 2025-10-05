#!/usr/bin/env python3
"""
Test runner for NASA-COMP weather integration tests.
Run this script to execute all weather integration tests.
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_weather_integration import WeatherIntegrationTester
from test_city_weather_integration import CityWeatherIntegrationTester
from test_groq_integration import main as test_groq_main

def main():
    """Run all weather integration tests."""
    print("🚀 Starting NASA-COMP Weather Integration Tests")
    print("=" * 60)
    
    # Check if server is running
    tester = WeatherIntegrationTester()
    
    # Run connectivity test first
    if not tester.test_server_connectivity():
        print("\n❌ Server is not running!")
        print("Please start the server with: uvicorn api_server:app --reload --host 0.0.0.0 --port 8000")
        return 1
    
    print("\n" + "="*60)
    print("🧪 Running Basic Weather Integration Tests")
    print("="*60)
    
    # Run basic weather integration tests
    basic_results = tester.run_all_tests()
    
    print("\n" + "="*60)
    print("🏙️ Running City-Based Weather Integration Tests")
    print("="*60)
    
    # Run city-based weather integration tests
    city_tester = CityWeatherIntegrationTester()
    city_results = city_tester.run_all_tests()
    
    print("\n" + "="*60)
    print("🧠 Running GROQ AI Integration Tests")
    print("="*60)
    
    # Run GROQ integration tests
    groq_result = test_groq_main()
    groq_passed = 1 if groq_result == 0 else 0
    groq_total = 1
    
    # Combine results
    total_tests = basic_results['total_tests'] + city_results['total_tests'] + groq_total
    total_passed = basic_results['passed_tests'] + city_results['passed_tests'] + groq_passed
    total_failed = basic_results['failed_tests'] + city_results['failed_tests'] + (groq_total - groq_passed)
    overall_success_rate = (total_passed / total_tests) * 100
    
    # Print combined summary
    print("\n" + "="*60)
    print("📈 Combined Test Summary")
    print("="*60)
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {total_passed}")
    print(f"   Failed: {total_failed}")
    print(f"   Overall Success Rate: {overall_success_rate:.1f}%")
    
    if total_failed == 0:
        print("\n🎉 All weather integration tests passed!")
        print("✨ The system is ready for AI-powered weather analysis!")
        print("🧠 GROQ AI integration provides intelligent interpretations")
        print("🏙️ City-based weather analysis with commute optimization")
    else:
        print(f"\n⚠️ {total_failed} tests failed. Please check the issues above.")
    
    return 0 if total_failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
