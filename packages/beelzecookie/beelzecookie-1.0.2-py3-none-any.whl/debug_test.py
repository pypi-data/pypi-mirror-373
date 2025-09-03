#!/usr/bin/env python3
"""
Debug script to test BeelzeCookie with 431 error detection
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from request_engine import RequestEngine
from analyzer import Analyzer

def debug_test():
    """Debug test for 431 error detection"""
    
    # Initialize components
    request_engine = RequestEngine()
    analyzer = Analyzer()
    
    # Test URL with large payload
    url = "http://localhost:5000/vulnerable"
    param = "gclid"
    payload = "A" * 4000  # 4000 character payload
    
    print(f"Testing URL: {url}")
    print(f"Parameter: {param}")
    print(f"Payload length: {len(payload)}")
    print("-" * 50)
    
    # Perform full test
    result = request_engine.full_test(url, param, payload, live_test=True)
    
    print("Raw Result:")
    print(f"  first_status: {result.get('first_status')}")
    print(f"  second_status: {result.get('second_status')}")
    print(f"  error_occurred: {result.get('error_occurred')}")
    print(f"  set_cookies: {len(result.get('set_cookies', []))}")
    print(f"  has_param_cookie: {result.get('has_param_cookie')}")
    print(f"  cookie_size_increase: {result.get('cookie_size_increase')}")
    print("-" * 50)
    
    # Analyze result
    analysis = analyzer.analyze_result(result)
    
    print("Analysis:")
    print(f"  risk_level: {analysis.get('risk_level')}")
    print(f"  summary: {analysis.get('summary')}")
    print(f"  error_detected: {analysis.get('error_detected')}")
    print(f"  error_type: {analysis.get('error_type')}")
    print(f"  risk_score: {analysis.get('risk_score')}")
    print(f"  risk_factors: {analysis.get('risk_factors')}")
    
    # Check if 431 is in error status codes
    print(f"\n431 in error_status_codes: {431 in analyzer.error_status_codes}")
    
    # Test with dry run
    print("\n" + "="*50)
    print("DRY RUN TEST")
    print("="*50)
    
    dry_result = request_engine.dry_run_test(url, param, payload)
    
    print("Dry Run Result:")
    print(f"  first_status: {dry_result.get('first_status')}")
    print(f"  set_cookies: {len(dry_result.get('set_cookies', []))}")
    print(f"  has_param_cookie: {dry_result.get('has_param_cookie')}")
    
    dry_analysis = analyzer.analyze_result(dry_result)
    print(f"  risk_level: {dry_analysis.get('risk_level')}")
    print(f"  error_detected: {dry_analysis.get('error_detected')}")

if __name__ == "__main__":
    debug_test() 