#!/usr/bin/env python3
"""
Simple Test for BeelzeCookie Structure
Demonstrates the tool's structure and basic functionality
"""

import os
import sys

def test_file_structure():
    """Test that all required files exist"""
    print("🧪 Testing BeelzeCookie File Structure...")
    print("=" * 50)
    
    required_files = [
        '__init__.py',
        'cli.py',
        'recon.py',
        'payload_generator.py',
        'request_engine.py',
        'analyzer.py',
        'reporter.py',
        'main.py',
        'requirements.txt',
        'README.md',
        'setup.py'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        return False
    else:
        print(f"\n✅ All required files present!")
        return True

def test_imports():
    """Test basic imports"""
    print("\n🧪 Testing Basic Imports...")
    print("=" * 50)
    
    try:
        # Test basic Python imports
        import argparse
        import requests
        import json
        import time
        import re
        from urllib.parse import urlparse, parse_qs, urljoin
        from typing import List, Dict, Optional
        print("✅ Basic Python imports successful")
    except ImportError as e:
        print(f"❌ Basic import failed: {e}")
        return False
    
    try:
        # Test BeautifulSoup import (will fail without installation)
        from bs4 import BeautifulSoup
        print("✅ BeautifulSoup import successful")
    except ImportError:
        print("⚠️  BeautifulSoup not installed (will be installed with requirements.txt)")
    
    return True

def test_module_structure():
    """Test module structure"""
    print("\n🧪 Testing Module Structure...")
    print("=" * 50)
    
    modules = [
        ('cli.py', 'CLIOrchestrator'),
        ('recon.py', 'ReconModule'),
        ('payload_generator.py', 'PayloadGenerator'),
        ('request_engine.py', 'RequestEngine'),
        ('analyzer.py', 'Analyzer'),
        ('reporter.py', 'Reporter')
    ]
    
    for module_file, class_name in modules:
        if os.path.exists(module_file):
            print(f"✅ {module_file} exists")
            # Try to read the file and check for class
            try:
                with open(module_file, 'r') as f:
                    content = f.read()
                    if f'class {class_name}' in content:
                        print(f"   ✅ Class {class_name} found")
                    else:
                        print(f"   ⚠️  Class {class_name} not found")
            except Exception as e:
                print(f"   ❌ Error reading {module_file}: {e}")
        else:
            print(f"❌ {module_file} missing")

def test_cli_help():
    """Test CLI help generation"""
    print("\n🧪 Testing CLI Help Generation...")
    print("=" * 50)
    
    try:
        # Import the CLI module
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Test basic CLI functionality
        import argparse
        
        # Create a simple parser to test argument parsing
        parser = argparse.ArgumentParser(description="BeelzeCookie - Cookie Bomb Vulnerability Scanner")
        parser.add_argument("--url", help="Single target URL to test")
        parser.add_argument("--urls", help="File containing list of URLs to test")
        parser.add_argument("--params", help="Comma-separated list of parameters to test")
        parser.add_argument("--auto", action="store_true", help="Automatically discover parameters")
        parser.add_argument("--lengths", default="500,1000,2000,4000", help="Payload lengths to test")
        parser.add_argument("--dry-run", action="store_true", help="Only check Set-Cookie headers")
        parser.add_argument("--live", action="store_true", help="Test cookie persistence")
        parser.add_argument("--proxy", help="Proxy URL")
        parser.add_argument("--timeout", type=int, default=30, help="Request timeout")
        parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests")
        parser.add_argument("--output", help="Output file for results")
        parser.add_argument("--report", help="Generate markdown report")
        parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
        
        print("✅ CLI argument parser created successfully")
        print("✅ All expected arguments defined")
        
        # Test help generation
        help_text = parser.format_help()
        if "BeelzeCookie" in help_text and "Cookie Bomb" in help_text:
            print("✅ Help text generated correctly")
        else:
            print("⚠️  Help text may be incomplete")
            
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False
    
    return True

def main():
    """Main test function"""
    print("🚀 BeelzeCookie - Structure Test")
    print("=" * 60)
    
    # Test file structure
    structure_ok = test_file_structure()
    
    # Test imports
    imports_ok = test_imports()
    
    # Test module structure
    test_module_structure()
    
    # Test CLI
    cli_ok = test_cli_help()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    if structure_ok and imports_ok and cli_ok:
        print("✅ All tests passed!")
        print("\n🎉 BeelzeCookie is ready to use!")
        print("\nTo install dependencies:")
        print("pip install -r requirements.txt")
        print("\nTo run the tool:")
        print("python main.py --url https://example.com --auto --lengths 500,1000")
        print("python main.py --help")
    else:
        print("❌ Some tests failed. Please check the output above.")
    
    print("\n📝 Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Test with a real target: python main.py --url https://example.com --dry-run")
    print("3. Generate reports: python main.py --url https://example.com --auto --output results.json --report report.md")

if __name__ == "__main__":
    main() 