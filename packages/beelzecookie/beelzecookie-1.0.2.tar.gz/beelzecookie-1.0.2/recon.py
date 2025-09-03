"""
Reconnaissance Module - Parameter Discovery
Discovers potential parameters from target URLs using various techniques
"""

import re
import requests
from urllib.parse import urlparse, parse_qs, urljoin
from typing import List, Set, Optional
from bs4 import BeautifulSoup
import json


class ReconModule:
    def __init__(self):
        # Known tracking parameters that are commonly vulnerable to cookie bombs
        self.known_tracking_params = {
            'gclid', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
            'fbclid', 'dclid', 'msclkid', 'mc_cid', 'mc_eid', 'ref', 'source', 'campaign',
            'affiliate', 'partner', 'referrer', 'referral', 'tracking', 'track', 'id',
            'session', 'user', 'visitor', 'client', 'customer', 'member', 'account',
            'email', 'mail', 'newsletter', 'subscribe', 'signup', 'register', 'login',
            'auth', 'token', 'key', 'api', 'apikey', 'secret', 'password', 'pass',
            'redirect', 'return', 'next', 'target', 'destination', 'url', 'link',
            'click', 'cta', 'button', 'action', 'event', 'goal', 'conversion',
            'purchase', 'buy', 'order', 'cart', 'basket', 'checkout', 'payment',
            'product', 'item', 'category', 'tag', 'label', 'brand', 'vendor',
            'price', 'cost', 'discount', 'coupon', 'promo', 'offer', 'deal',
            'search', 'query', 'q', 'keyword', 'term', 'phrase', 'filter',
            'sort', 'order', 'page', 'limit', 'offset', 'start', 'end',
            'date', 'time', 'timestamp', 'created', 'updated', 'modified',
            'status', 'state', 'condition', 'type', 'format', 'mode',
            'lang', 'language', 'locale', 'region', 'country', 'currency',
            'device', 'platform', 'browser', 'os', 'mobile', 'desktop',
            'ip', 'geo', 'location', 'city', 'state', 'zip', 'postal'
        }

        # Common parameter patterns in URLs
        self.param_patterns = [
            r'[?&]([a-zA-Z_][a-zA-Z0-9_]*)=',
            r'data-([a-zA-Z-]+)=',
            r'js-([a-zA-Z-]+)=',
            r'track-([a-zA-Z-]+)=',
            r'analytics-([a-zA-Z-]+)='
        ]

    def discover_parameters(self, url: str) -> List[str]:
        """
        Discover potential parameters from a target URL
        Returns a list of parameter names
        """
        discovered_params = set()

        # Method 1: Extract from URL itself
        discovered_params.update(self._extract_from_url(url))

        # Method 2: Fetch and parse HTML/JS
        discovered_params.update(self._extract_from_html(url))

        # Method 3: Check for common tracking parameters
        discovered_params.update(self._check_known_params(url))

        # Method 4: Extract from JavaScript files
        discovered_params.update(self._extract_from_js(url))

        # Method 5: Check for API endpoints
        discovered_params.update(self._extract_from_apis(url))

        return list(discovered_params)

    def _extract_from_url(self, url: str) -> Set[str]:
        """Extract parameters from the URL itself"""
        params = set()
        
        try:
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            params.update(query_params.keys())
            
            # Also check for parameters in path segments
            path_segments = parsed.path.split('/')
            for segment in path_segments:
                if '=' in segment:
                    param_part = segment.split('=')[0]
                    if param_part and param_part.isalnum():
                        params.add(param_part)
        except Exception:
            pass

        return params

    def _extract_from_html(self, url: str) -> Set[str]:
        """Extract parameters from HTML content"""
        params = set()
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract from form inputs
            for form in soup.find_all('form'):
                for input_tag in form.find_all('input'):
                    name = input_tag.get('name')
                    if name:
                        params.add(name)
                
                for select_tag in form.find_all('select'):
                    name = select_tag.get('name')
                    if name:
                        params.add(name)

            # Extract from links
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('?'):
                    href = 'http://example.com' + href
                elif not href.startswith(('http://', 'https://')):
                    href = urljoin(url, href)
                
                try:
                    parsed = urlparse(href)
                    query_params = parse_qs(parsed.query)
                    params.update(query_params.keys())
                except Exception:
                    pass

            # Extract from data attributes
            for tag in soup.find_all(attrs=True):
                for attr_name, attr_value in tag.attrs.items():
                    if attr_name.startswith('data-') and '=' in str(attr_value):
                        # Look for parameter-like patterns in data attributes
                        matches = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)=', str(attr_value))
                        params.update(matches)

            # Extract from inline JavaScript
            for script in soup.find_all('script'):
                if script.string:
                    params.update(self._extract_params_from_js(script.string))

        except Exception as e:
            print(f"[-] Error extracting from HTML: {e}")

        return params

    def _extract_from_js(self, url: str) -> Set[str]:
        """Extract parameters from JavaScript files"""
        params = set()
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find JavaScript files
            for script in soup.find_all('script', src=True):
                js_url = script['src']
                if not js_url.startswith(('http://', 'https://')):
                    js_url = urljoin(url, js_url)
                
                try:
                    js_response = requests.get(js_url, headers=headers, timeout=10)
                    if js_response.status_code == 200:
                        params.update(self._extract_params_from_js(js_response.text))
                except Exception:
                    pass

        except Exception as e:
            print(f"[-] Error extracting from JS: {e}")

        return params

    def _extract_params_from_js(self, js_content: str) -> Set[str]:
        """Extract parameter names from JavaScript content"""
        params = set()
        
        # Common patterns for URL parameters in JavaScript
        patterns = [
            r'[?&]([a-zA-Z_][a-zA-Z0-9_]*)=',
            r'getParameter\([\'"]([a-zA-Z_][a-zA-Z0-9_]*)[\'"]\)',
            r'searchParams\.get\([\'"]([a-zA-Z_][a-zA-Z0-9_]*)[\'"]\)',
            r'[\'"]([a-zA-Z_][a-zA-Z0-9_]*)[\'"]\s*[:=]\s*[\'"][^\'"]*[\'"]',
            r'params\[[\'"]([a-zA-Z_][a-zA-Z0-9_]*)[\'"]\]',
            r'query\[[\'"]([a-zA-Z_][a-zA-Z0-9_]*)[\'"]\]'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, js_content)
            params.update(matches)
        
        return params

    def _check_known_params(self, url: str) -> Set[str]:
        """Check if known tracking parameters are present in the URL"""
        params = set()
        
        # Check if any known parameters are already in the URL
        for param in self.known_tracking_params:
            if f'{param}=' in url:
                params.add(param)
        
        return params

    def _extract_from_apis(self, url: str) -> Set[str]:
        """Extract parameters from potential API endpoints"""
        params = set()
        
        try:
            # Common API endpoint patterns
            api_patterns = [
                '/api/', '/rest/', '/graphql', '/v1/', '/v2/', '/v3/',
                '/endpoint/', '/service/', '/data/', '/json/', '/xml/'
            ]
            
            parsed = urlparse(url)
            path = parsed.path.lower()
            
            if any(pattern in path for pattern in api_patterns):
                # If it looks like an API, add common API parameters
                api_params = {
                    'api_key', 'token', 'auth', 'key', 'secret', 'id',
                    'user_id', 'client_id', 'app_id', 'session_id',
                    'limit', 'offset', 'page', 'size', 'count',
                    'sort', 'order', 'filter', 'search', 'query',
                    'fields', 'include', 'exclude', 'expand'
                }
                params.update(api_params)
        
        except Exception:
            pass
        
        return params

    def get_common_tracking_params(self) -> List[str]:
        """Get list of common tracking parameters"""
        return list(self.known_tracking_params)

    def suggest_parameters(self, url: str) -> List[str]:
        """Suggest parameters based on URL analysis"""
        suggestions = []
        
        # Add discovered parameters
        discovered = self.discover_parameters(url)
        suggestions.extend(discovered)
        
        # Add common tracking parameters if not already discovered
        for param in self.known_tracking_params:
            if param not in discovered:
                suggestions.append(param)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_suggestions = []
        for param in suggestions:
            if param not in seen:
                seen.add(param)
                unique_suggestions.append(param)
        
        return unique_suggestions[:20]  # Limit to top 20 suggestions 