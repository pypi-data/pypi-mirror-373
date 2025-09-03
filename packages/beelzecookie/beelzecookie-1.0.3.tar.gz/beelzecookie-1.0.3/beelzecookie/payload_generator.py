"""
Payload Generator Module
Generates test payloads for cookie bomb testing
"""

import random
import string
from typing import List, Tuple, Dict
import itertools


class PayloadGenerator:
    def __init__(self):
        # Common tracking parameter values that might be used
        self.tracking_values = [
            'google', 'facebook', 'twitter', 'linkedin', 'instagram', 'youtube',
            'tiktok', 'snapchat', 'pinterest', 'reddit', 'discord', 'telegram',
            'whatsapp', 'email', 'sms', 'push', 'banner', 'popup', 'sidebar',
            'header', 'footer', 'content', 'article', 'product', 'category',
            'search', 'homepage', 'landing', 'checkout', 'payment', 'success',
            'error', '404', 'login', 'register', 'profile', 'dashboard',
            'admin', 'user', 'guest', 'anonymous', 'premium', 'vip', 'gold',
            'silver', 'bronze', 'free', 'trial', 'demo', 'test', 'dev', 'staging'
        ]

        # Common UTM values
        self.utm_sources = ['google', 'facebook', 'twitter', 'linkedin', 'instagram', 'email', 'direct', 'organic']
        self.utm_mediums = ['cpc', 'cpm', 'email', 'social', 'banner', 'popup', 'referral', 'organic']
        self.utm_campaigns = ['summer_sale', 'black_friday', 'christmas', 'new_year', 'spring_cleaning', 'holiday_special']

    def generate_payloads(self, parameter: str, lengths: List[int]) -> List[Tuple[int, str]]:
        """
        Generate payloads for a specific parameter with different lengths
        Returns list of (length, payload) tuples
        """
        payloads = []
        
        for length in lengths:
            # Generate different types of payloads
            payloads.extend([
                (length, self._generate_random_string(length)),
                (length, self._generate_repeating_pattern(length)),
                (length, self._generate_tracking_like_payload(parameter, length)),
                (length, self._generate_encoded_payload(length))
            ])
        
        return payloads

    def generate_combination_payloads(self, parameters: List[str], lengths: List[int]) -> List[Tuple[List[str], Dict[str, str]]]:
        """
        Generate payloads for testing multiple parameters simultaneously
        Returns list of (parameter_list, payload_dict) tuples
        """
        combinations = []
        
        # Test combinations of 2-3 parameters at a time
        for combo_size in range(2, min(4, len(parameters) + 1)):
            for param_combo in itertools.combinations(parameters, combo_size):
                for length in lengths:
                    payload_dict = {}
                    for param in param_combo:
                        payload_dict[param] = self._generate_tracking_like_payload(param, length)
                    
                    combinations.append((list(param_combo), payload_dict))
        
        return combinations

    def _generate_random_string(self, length: int) -> str:
        """Generate a random string of specified length"""
        # Use alphanumeric characters that are safe for URLs
        chars = string.ascii_letters + string.digits + '-_'
        return ''.join(random.choice(chars) for _ in range(length))

    def _generate_repeating_pattern(self, length: int) -> str:
        """Generate a repeating pattern payload"""
        # Create a pattern that repeats to reach the desired length
        base_pattern = "A" * 100  # 100 character base pattern
        repetitions = length // len(base_pattern)
        remainder = length % len(base_pattern)
        
        payload = base_pattern * repetitions + base_pattern[:remainder]
        return payload

    def _generate_tracking_like_payload(self, parameter: str, length: int) -> str:
        """Generate a payload that looks like real tracking data"""
        if parameter.startswith('utm_'):
            return self._generate_utm_like_payload(parameter, length)
        elif parameter in ['gclid', 'fbclid', 'dclid', 'msclkid']:
            return self._generate_clid_like_payload(length)
        elif parameter in ['ref', 'source', 'campaign']:
            return self._generate_campaign_like_payload(length)
        else:
            return self._generate_generic_tracking_payload(parameter, length)

    def _generate_utm_like_payload(self, parameter: str, length: int) -> str:
        """Generate UTM-like payloads"""
        if parameter == 'utm_source':
            base = random.choice(self.utm_sources)
        elif parameter == 'utm_medium':
            base = random.choice(self.utm_mediums)
        elif parameter == 'utm_campaign':
            base = random.choice(self.utm_campaigns)
        else:
            base = 'tracking'
        
        # Extend the base to reach desired length
        if len(base) >= length:
            return base[:length]
        
        # Add random characters to reach the target length
        remaining = length - len(base)
        suffix = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(remaining))
        
        return base + suffix

    def _generate_clid_like_payload(self, length: int) -> str:
        """Generate CLID-like payloads (Google, Facebook, etc.)"""
        # CLID format: usually base64-like strings
        chars = string.ascii_letters + string.digits + '-_'
        return ''.join(random.choice(chars) for _ in range(length))

    def _generate_campaign_like_payload(self, length: int) -> str:
        """Generate campaign-like payloads"""
        base = random.choice(self.tracking_values)
        
        if len(base) >= length:
            return base[:length]
        
        # Add campaign-like suffixes
        suffixes = ['_2024', '_campaign', '_promo', '_offer', '_deal', '_sale']
        suffix = random.choice(suffixes)
        
        remaining = length - len(base) - len(suffix)
        if remaining > 0:
            middle = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(remaining))
            return base + middle + suffix
        else:
            return base + suffix[:remaining]

    def _generate_generic_tracking_payload(self, parameter: str, length: int) -> str:
        """Generate generic tracking payloads"""
        # Create a payload that includes the parameter name
        base = f"{parameter}_tracking"
        
        if len(base) >= length:
            return base[:length]
        
        # Add random tracking-like content
        remaining = length - len(base)
        tracking_content = ''.join(random.choice(string.ascii_lowercase + string.digits + '_') for _ in range(remaining))
        
        return base + tracking_content

    def _generate_encoded_payload(self, length: int) -> str:
        """Generate URL-encoded payloads"""
        # Create a payload with URL encoding
        base_content = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length // 3))
        
        # URL encode some characters
        encoded = base_content.replace('a', '%61').replace('e', '%65').replace('i', '%69')
        
        # Pad to reach desired length
        while len(encoded) < length:
            encoded += '%' + random.choice('0123456789abcdef')
        
        return encoded[:length]

    def generate_specialized_payloads(self, parameter: str, length: int) -> List[str]:
        """Generate specialized payloads for specific parameter types"""
        payloads = []
        
        # Base64-like payloads
        payloads.append(self._generate_base64_like_payload(length))
        
        # JSON-like payloads
        payloads.append(self._generate_json_like_payload(parameter, length))
        
        # XML-like payloads
        payloads.append(self._generate_xml_like_payload(parameter, length))
        
        # URL-encoded payloads
        payloads.append(self._generate_url_encoded_payload(length))
        
        return payloads

    def _generate_base64_like_payload(self, length: int) -> str:
        """Generate base64-like payloads"""
        chars = string.ascii_letters + string.digits + '+/'
        return ''.join(random.choice(chars) for _ in range(length))

    def _generate_json_like_payload(self, parameter: str, length: int) -> str:
        """Generate JSON-like payloads"""
        json_template = f'{{"{parameter}":"VALUE"}}'
        
        if len(json_template) >= length:
            return json_template[:length]
        
        # Fill with JSON-like content
        remaining = length - len(json_template)
        json_content = f'"{parameter}":"' + 'A' * (remaining - 4) + '"'
        
        return '{' + json_content + '}'

    def _generate_xml_like_payload(self, parameter: str, length: int) -> str:
        """Generate XML-like payloads"""
        xml_template = f'<{parameter}>VALUE</{parameter}>'
        
        if len(xml_template) >= length:
            return xml_template[:length]
        
        # Fill with XML-like content
        remaining = length - len(xml_template)
        xml_content = 'A' * remaining
        
        return f'<{parameter}>{xml_content}</{parameter}>'

    def _generate_url_encoded_payload(self, length: int) -> str:
        """Generate URL-encoded payloads"""
        # Create a payload with various URL encodings
        content = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length // 4))
        
        # Apply various encodings
        encoded = content.replace('a', '%61').replace('e', '%65').replace('i', '%69').replace('o', '%6F').replace('u', '%75')
        
        # Pad with more encoded characters
        while len(encoded) < length:
            encoded += '%' + ''.join(random.choice('0123456789abcdef') for _ in range(2))
        
        return encoded[:length]

    def get_payload_statistics(self, payloads: List[Tuple[int, str]]) -> Dict:
        """Get statistics about generated payloads"""
        stats = {
            'total_payloads': len(payloads),
            'unique_lengths': len(set(length for length, _ in payloads)),
            'min_length': min(length for length, _ in payloads) if payloads else 0,
            'max_length': max(length for length, _ in payloads) if payloads else 0,
            'avg_length': sum(length for length, _ in payloads) / len(payloads) if payloads else 0,
            'lengths': sorted(list(set(length for length, _ in payloads)))
        }
        
        return stats 