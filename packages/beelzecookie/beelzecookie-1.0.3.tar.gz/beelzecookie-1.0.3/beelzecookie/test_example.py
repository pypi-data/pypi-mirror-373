#!/usr/bin/env python3
"""
Test Example for BeelzeCookie
Demonstrates the tool's functionality with a simple example
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from .recon import ReconModule
    from .payload_generator import PayloadGenerator
    from .request_engine import RequestEngine
    from .analyzer import Analyzer
    from .reporter import Reporter
except ImportError:
    from recon import ReconModule
    from payload_generator import PayloadGenerator
    from request_engine import RequestEngine
    from analyzer import Analyzer
    from reporter import Reporter

def test_basic_functionality():
    """Test basic functionality of all modules"""
    print("🧪 Testing BeelzeCookie Modules...")
    print("=" * 50)
    
    # Test Recon Module
    print("\n1. Testing Recon Module...")
    recon = ReconModule()
    common_params = recon.get_common_tracking_params()
    print(f"   Found {len(common_params)} common tracking parameters")
    print(f"   Sample parameters: {common_params[:5]}")
    
    # Test Payload Generator
    print("\n2. Testing Payload Generator...")
    payload_gen = PayloadGenerator()
    test_params = ['gclid', 'utm_source']
    test_lengths = [500, 1000]
    
    for param in test_params:
        payloads = payload_gen.generate_payloads(param, test_lengths)
        print(f"   Generated {len(payloads)} payloads for {param}")
        print(f"   Sample payload: {payloads[0] if payloads else 'None'}")
    
    # Test Request Engine
    print("\n3. Testing Request Engine...")
    request_engine = RequestEngine()
    print(f"   Default timeout: {request_engine.timeout}s")
    print(f"   Default delay: {request_engine.delay}s")
    
    # Test Analyzer
    print("\n4. Testing Analyzer...")
    analyzer = Analyzer()
    print(f"   Error status codes: {analyzer.error_status_codes}")
    print(f"   Cookie size thresholds: {analyzer.cookie_size_thresholds}")
    
    # Test Reporter
    print("\n5. Testing Reporter...")
    reporter = Reporter()
    print("   Reporter initialized successfully")
    
    print("\n✅ All modules tested successfully!")
    print("\nTo run a real scan, use:")
    print("python main.py --url https://example.com --auto --lengths 500,1000")
    print("python main.py --help")

def test_mock_analysis():
    """Test the analyzer with mock data"""
    print("\n🧪 Testing Analysis with Mock Data...")
    print("=" * 50)
    
    analyzer = Analyzer()
    
    # Mock result data
    mock_result = {
        'url': 'https://example.com?gclid=test',
        'parameter': 'gclid',
        'payload_length': 1000,
        'first_status': 200,
        'second_status': 400,
        'set_cookies': ['gclid=test; Path=/'],
        'has_param_cookie': True,
        'cookie_size_increase': 1500,
        'error_occurred': False
    }
    
    # Analyze the mock result
    analysis = analyzer.analyze_result(mock_result)
    
    print(f"Risk Level: {analysis['risk_level']}")
    print(f"Summary: {analysis['summary']}")
    print(f"Risk Score: {analysis.get('risk_score', 'N/A')}")
    print(f"Risk Factors: {analysis.get('risk_factors', [])}")
    print(f"Cookie Size Increase: {analysis.get('cookie_size_increase', 0)} bytes")
    print(f"Cookie Persistence: {analysis.get('cookie_persistence', False)}")
    print(f"Error Detected: {analysis.get('error_detected', False)}")
    
    print("\n✅ Mock analysis completed!")

if __name__ == "__main__":
    test_basic_functionality()
    test_mock_analysis() 