"""
Request Engine Module
Handles HTTP requests, cookie management, and proxy support
"""

import requests
import time
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from typing import Dict, Optional, List, Tuple
import json
import random


class RequestEngine:
    def __init__(self):


        # Initialize the session
        user_agent_list = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/91.0.4472.124',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/91.0.4472.124',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.4472.124',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.4472.124',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/91.0.4472.124',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/91.0.4472.124',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.4472.124',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.4472.124',
        ]
        self.session = requests.Session()
        self.proxy = None
        self.timeout = 30
        self.delay = 1.0
        self.max_retries = 3
        
        # Default headers
        self.session.headers.update({
            'User-Agent': user_agent_list[random.randint(0, len(user_agent_list) - 1)],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    def set_proxy(self, proxy_url: str):
        """Set proxy for requests"""
        self.proxy = {
            'http': proxy_url,
            'https': proxy_url
        }
        self.session.proxies = self.proxy

    def set_timeout(self, timeout: int):
        """Set request timeout"""
        self.timeout = timeout

    def set_delay(self, delay: float):
        """Set delay between requests"""
        self.delay = delay

    def set_headers(self, headers: Dict[str, str]):
        """Set custom headers"""
        self.session.headers.update(headers)

    def build_url_with_param(self, base_url: str, param: str, value: str) -> str:
        """Build URL with parameter and value"""
        parsed = urlparse(base_url)
        query_params = parse_qs(parsed.query)
        
        # Add or update the parameter
        query_params[param] = [value]
        
        # Rebuild the URL
        new_query = urlencode(query_params, doseq=True)
        new_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
        
        return new_url

    def dry_run_test(self, url: str, param: str, payload: str) -> Dict:
        """
        Dry run test - only check for Set-Cookie headers
        No exploitation, just reconnaissance
        """
        test_url = self.build_url_with_param(url, param, payload)
        
        try:
            # Clear any existing cookies
            self.session.cookies.clear()
            
            # Make the request
            response = self.session.get(
                test_url,
                timeout=self.timeout,
                allow_redirects=True
            )
            
            # Extract Set-Cookie headers
            set_cookies = response.headers.getlist('Set-Cookie') if hasattr(response.headers, 'getlist') else response.headers.get('Set-Cookie', '').split(',') if response.headers.get('Set-Cookie') else []
            if not set_cookies:
                set_cookies = []
            
            # Check if any cookie contains the parameter name
            param_cookies = []
            for cookie in set_cookies:
                if param.lower() in cookie.lower():
                    param_cookies.append(cookie)
            
            result = {
                'url': test_url,
                'parameter': param,
                'payload_length': len(payload),
                'first_status': response.status_code,
                'set_cookies': set_cookies,
                'param_cookies': param_cookies,
                'has_param_cookie': len(param_cookies) > 0,
                'cookie_count': len(set_cookies),
                'response_size': len(response.content),
                'headers': dict(response.headers)
            }
            
            # Add delay
            time.sleep(self.delay)
            
            return result
            
        except requests.exceptions.RequestException as e:
            return {
                'url': test_url,
                'parameter': param,
                'payload_length': len(payload),
                'error': str(e),
                'first_status': None,
                'set_cookies': [],
                'param_cookies': [],
                'has_param_cookie': False,
                'cookie_count': 0,
                'response_size': 0,
                'headers': {}
            }

    def full_test(self, url: str, param: str, payload: str, live_test: bool = False) -> Dict:
        """
        Full test - check Set-Cookie and test cookie persistence
        """
        test_url = self.build_url_with_param(url, param, payload)
        
        try:
            # Clear any existing cookies
            self.session.cookies.clear()
            
            # First request - check for Set-Cookie
            first_response = self.session.get(
                test_url,
                timeout=self.timeout,
                allow_redirects=True
            )
            
            # Extract Set-Cookie headers
            set_cookies = first_response.headers.getlist('Set-Cookie') if hasattr(first_response.headers, 'getlist') else first_response.headers.get('Set-Cookie', '').split(',') if first_response.headers.get('Set-Cookie') else []
            if not set_cookies:
                set_cookies = []
            
            # Check if any cookie contains the parameter name
            param_cookies = []
            for cookie in set_cookies:
                if param.lower() in cookie.lower():
                    param_cookies.append(cookie)
            
            # Calculate cookie sizes
            first_cookie_size = self._calculate_cookie_size(self.session.cookies)
            
            # Add delay
            time.sleep(self.delay)
            
            # Second request - test cookie persistence and error conditions
            second_response = None
            second_status = None
            second_cookie_size = 0
            error_occurred = False
            
            if live_test and self.session.cookies:
                try:
                    second_response = self.session.get(
                        url,  # Use original URL for second request
                        timeout=self.timeout,
                        allow_redirects=True
                    )
                    second_status = second_response.status_code
                    second_cookie_size = self._calculate_cookie_size(self.session.cookies)
                except requests.exceptions.RequestException as e:
                    error_occurred = True
                    second_status = 'ERROR'
            
            result = {
                'url': test_url,
                'parameter': param,
                'payload_length': len(payload),
                'first_status': first_response.status_code,
                'second_status': second_status,
                'set_cookies': set_cookies,
                'param_cookies': param_cookies,
                'has_param_cookie': len(param_cookies) > 0,
                'cookie_count': len(set_cookies),
                'first_cookie_size': first_cookie_size,
                'second_cookie_size': second_cookie_size,
                'cookie_size_increase': second_cookie_size - first_cookie_size if second_cookie_size > 0 else 0,
                'response_size': len(first_response.content),
                'error_occurred': error_occurred,
                'headers': dict(first_response.headers)
            }
            
            # Add delay
            time.sleep(self.delay)
            
            return result
            
        except requests.exceptions.RequestException as e:
            return {
                'url': test_url,
                'parameter': param,
                'payload_length': len(payload),
                'error': str(e),
                'first_status': None,
                'second_status': None,
                'set_cookies': [],
                'param_cookies': [],
                'has_param_cookie': False,
                'cookie_count': 0,
                'first_cookie_size': 0,
                'second_cookie_size': 0,
                'cookie_size_increase': 0,
                'response_size': 0,
                'error_occurred': True,
                'headers': {}
            }

    def _calculate_cookie_size(self, cookies) -> int:
        """Calculate the total size of cookies in bytes"""
        total_size = 0
        for cookie in cookies:
            # Calculate size of cookie name and value
            total_size += len(cookie.name) + len(cookie.value)
            # Add size of separators and other cookie attributes
            total_size += 10  # Approximate overhead for cookie formatting
        return total_size

    def test_multiple_params(self, url: str, params: Dict[str, str]) -> Dict:
        """
        Test multiple parameters simultaneously
        """
        # Build URL with multiple parameters
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        # Add all parameters
        for param, value in params.items():
            query_params[param] = [value]
        
        # Rebuild the URL
        new_query = urlencode(query_params, doseq=True)
        test_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
        
        try:
            # Clear any existing cookies
            self.session.cookies.clear()
            
            # First request
            first_response = self.session.get(
                test_url,
                timeout=self.timeout,
                allow_redirects=True
            )
            
            # Extract Set-Cookie headers
            set_cookies = first_response.headers.getlist('Set-Cookie') if hasattr(first_response.headers, 'getlist') else first_response.headers.get('Set-Cookie', '').split(',') if first_response.headers.get('Set-Cookie') else []
            if not set_cookies:
                set_cookies = []
            
            # Check for parameter cookies
            param_cookies = []
            for cookie in set_cookies:
                for param in params.keys():
                    if param.lower() in cookie.lower():
                        param_cookies.append(cookie)
                        break
            
            first_cookie_size = self._calculate_cookie_size(self.session.cookies)
            
            # Add delay
            time.sleep(self.delay)
            
            # Second request
            second_response = None
            second_status = None
            second_cookie_size = 0
            
            if self.session.cookies:
                try:
                    second_response = self.session.get(
                        url,
                        timeout=self.timeout,
                        allow_redirects=True
                    )
                    second_status = second_response.status_code
                    second_cookie_size = self._calculate_cookie_size(self.session.cookies)
                except requests.exceptions.RequestException:
                    second_status = 'ERROR'
            
            result = {
                'url': test_url,
                'parameters': params,
                'total_payload_length': sum(len(v) for v in params.values()),
                'first_status': first_response.status_code,
                'second_status': second_status,
                'set_cookies': set_cookies,
                'param_cookies': param_cookies,
                'has_param_cookies': len(param_cookies) > 0,
                'cookie_count': len(set_cookies),
                'first_cookie_size': first_cookie_size,
                'second_cookie_size': second_cookie_size,
                'cookie_size_increase': second_cookie_size - first_cookie_size if second_cookie_size > 0 else 0,
                'response_size': len(first_response.content),
                'headers': dict(first_response.headers)
            }
            
            # Add delay
            time.sleep(self.delay)
            
            return result
            
        except requests.exceptions.RequestException as e:
            return {
                'url': test_url,
                'parameters': params,
                'total_payload_length': sum(len(v) for v in params.values()),
                'error': str(e),
                'first_status': None,
                'second_status': None,
                'set_cookies': [],
                'param_cookies': [],
                'has_param_cookies': False,
                'cookie_count': 0,
                'first_cookie_size': 0,
                'second_cookie_size': 0,
                'cookie_size_increase': 0,
                'response_size': 0,
                'headers': {}
            }

    def test_cookie_persistence(self, url: str, param: str, payload: str) -> Dict:
        """
        Test if cookies persist across multiple requests
        """
        test_url = self.build_url_with_param(url, param, payload)
        
        try:
            # Clear cookies
            self.session.cookies.clear()
            
            # First request
            first_response = self.session.get(test_url, timeout=self.timeout)
            first_cookies = dict(self.session.cookies)
            
            time.sleep(self.delay)
            
            # Second request to original URL
            second_response = self.session.get(url, timeout=self.timeout)
            second_cookies = dict(self.session.cookies)
            
            time.sleep(self.delay)
            
            # Third request to original URL
            third_response = self.session.get(url, timeout=self.timeout)
            third_cookies = dict(self.session.cookies)
            
            # Check persistence
            cookies_persist = len(second_cookies) > 0 and len(third_cookies) > 0
            
            result = {
                'url': test_url,
                'parameter': param,
                'payload_length': len(payload),
                'first_cookies': first_cookies,
                'second_cookies': second_cookies,
                'third_cookies': third_cookies,
                'cookies_persist': cookies_persist,
                'cookie_count_first': len(first_cookies),
                'cookie_count_second': len(second_cookies),
                'cookie_count_third': len(third_cookies),
                'first_status': first_response.status_code,
                'second_status': second_response.status_code,
                'third_status': third_response.status_code
            }
            
            return result
            
        except requests.exceptions.RequestException as e:
            return {
                'url': test_url,
                'parameter': param,
                'payload_length': len(payload),
                'error': str(e),
                'cookies_persist': False,
                'cookie_count_first': 0,
                'cookie_count_second': 0,
                'cookie_count_third': 0,
                'first_status': None,
                'second_status': None,
                'third_status': None
            }

    def get_session_info(self) -> Dict:
        """Get current session information"""
        return {
            'proxy': self.proxy,
            'timeout': self.timeout,
            'delay': self.delay,
            'cookies': dict(self.session.cookies),
            'headers': dict(self.session.headers)
        } 