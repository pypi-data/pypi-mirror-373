"""
Analyzer Module - Result Analysis and Risk Scoring
Evaluates test results and provides risk assessment
"""

from typing import Dict, List, Optional
import re


class Analyzer:
    def __init__(self):
        # Error status codes that indicate cookie bomb vulnerability
        self.error_status_codes = {
            400,  # Bad Request - often indicates oversized cookies
            413,  # Payload Too Large
            414,  # URI Too Long
            431,  # Request Header Fields Too Large
            502,  # Bad Gateway
            503,  # Service Unavailable
            504   # Gateway Timeout
        }
        
        # Cookie size thresholds (in bytes)
        self.cookie_size_thresholds = {
            'low': 1000,      # 1KB
            'medium': 4000,   # 4KB
            'high': 8000      # 8KB
        }

    def analyze_result(self, result: Dict) -> Dict:
        """
        Analyze a test result and provide risk assessment
        """
        analysis = {
            'risk_level': 'Low',
            'summary': '',
            'details': [],
            'cookie_size_increase': 0,
            'cookie_persistence': False,
            'error_detected': False,
            'vulnerability_type': None,
            'recommendations': []
        }
        
        # Check for errors in the result
        if 'error' in result and result['error']:
            analysis['error_detected'] = True
            analysis['summary'] = f"Request failed: {result['error']}"
            analysis['details'].append(f"Request error: {result['error']}")
            return analysis
        
        # Analyze cookie behavior
        cookie_analysis = self._analyze_cookie_behavior(result)
        analysis.update(cookie_analysis)
        
        # Analyze HTTP status codes
        status_analysis = self._analyze_status_codes(result)
        analysis.update(status_analysis)
        
        # Analyze cookie size
        size_analysis = self._analyze_cookie_size(result)
        analysis.update(size_analysis)
        
        # Determine overall risk level
        risk_analysis = self._determine_risk_level(analysis)
        analysis.update(risk_analysis)
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        return analysis

    def _analyze_cookie_behavior(self, result: Dict) -> Dict:
        """Analyze cookie behavior patterns"""
        analysis = {
            'cookie_written': False,
            'param_cookie_detected': False,
            'cookie_persistence': False,
            'cookie_count': 0
        }
        
        # Check if cookies were set
        if result.get('set_cookies'):
            analysis['cookie_written'] = True
            analysis['cookie_count'] = len(result['set_cookies'])
        
        # Check if parameter-specific cookies were detected
        if result.get('has_param_cookie', False):
            analysis['param_cookie_detected'] = True
        
        # Check cookie persistence (if second request was made)
        if 'second_status' in result and result['second_status'] is not None:
            if result.get('cookie_size_increase', 0) > 0:
                analysis['cookie_persistence'] = True
        
        return analysis

    def _analyze_status_codes(self, result: Dict) -> Dict:
        """Analyze HTTP status codes for error patterns"""
        analysis = {
            'error_detected': False,
            'status_transition': None,
            'error_type': None
        }
        
        first_status = result.get('first_status')
        second_status = result.get('second_status')
        
        # Check for error status codes
        if first_status in self.error_status_codes:
            analysis['error_detected'] = True
            analysis['error_type'] = f"First request failed with status {first_status}"
        
        if second_status in self.error_status_codes:
            analysis['error_detected'] = True
            analysis['error_type'] = f"Second request failed with status {second_status}"
        
        # Analyze status transitions
        if first_status and second_status:
            if first_status == 200 and second_status in self.error_status_codes:
                analysis['status_transition'] = f"200 → {second_status}"
                analysis['error_detected'] = True
            elif first_status in self.error_status_codes and second_status in self.error_status_codes:
                analysis['status_transition'] = f"{first_status} → {second_status}"
                analysis['error_detected'] = True
        
        return analysis

    def _analyze_cookie_size(self, result: Dict) -> Dict:
        """Analyze cookie size patterns"""
        analysis = {
            'cookie_size_increase': 0,
            'size_category': 'normal',
            'size_risk': 'low'
        }
        
        # Get cookie size increase
        size_increase = result.get('cookie_size_increase', 0)
        analysis['cookie_size_increase'] = size_increase
        
        # Categorize size
        if size_increase == 0:
            analysis['size_category'] = 'no_increase'
            analysis['size_risk'] = 'low'
        elif size_increase <= self.cookie_size_thresholds['low']:
            analysis['size_category'] = 'small_increase'
            analysis['size_risk'] = 'low'
        elif size_increase <= self.cookie_size_thresholds['medium']:
            analysis['size_category'] = 'medium_increase'
            analysis['size_risk'] = 'medium'
        elif size_increase <= self.cookie_size_thresholds['high']:
            analysis['size_category'] = 'large_increase'
            analysis['size_risk'] = 'high'
        else:
            analysis['size_category'] = 'excessive_increase'
            analysis['size_risk'] = 'critical'
        
        return analysis

    def _determine_risk_level(self, analysis: Dict) -> Dict:
        """Determine overall risk level based on all factors"""
        risk_score = 0
        risk_factors = []
        
        # Factor 1: Cookie writing (base score)
        if analysis.get('cookie_written', False):
            risk_score += 1
            risk_factors.append("Cookies are being written")
        
        # Factor 2: Parameter-specific cookies
        if analysis.get('param_cookie_detected', False):
            risk_score += 2
            risk_factors.append("Parameter values are being written to cookies")
        
        # Factor 3: Cookie persistence
        if analysis.get('cookie_persistence', False):
            risk_score += 2
            risk_factors.append("Cookies persist across requests")
        
        # Factor 4: Error detection
        if analysis.get('error_detected', False):
            # Check for specific error types
            error_type = analysis.get('error_type', '')
            if '431' in error_type or 'Request Header Fields Too Large' in error_type:
                risk_score += 10  # Very high score for 431 errors (cookie bomb)
                risk_factors.append("HTTP 431 error detected (Cookie Bomb DoS)")
            else:
                risk_score += 8  # High score for other HTTP errors
                risk_factors.append("HTTP errors detected (potential DoS)")
        
        # Factor 5: Cookie size increase
        size_risk = analysis.get('size_risk', 'low')
        if size_risk == 'medium':
            risk_score += 1
            risk_factors.append("Significant cookie size increase")
        elif size_risk == 'high':
            risk_score += 2
            risk_factors.append("Large cookie size increase")
        elif size_risk == 'critical':
            risk_score += 3
            risk_factors.append("Excessive cookie size increase")
        
        # Factor 6: Status transitions
        if analysis.get('status_transition'):
            if '200 →' in analysis['status_transition']:
                risk_score += 2
                risk_factors.append("Successful request followed by error")
        
        # Determine risk level
        if risk_score >= 8:
            risk_level = 'High'
            vulnerability_type = 'Cookie Bomb (DoS)'
            summary = "High risk cookie bomb vulnerability detected. Parameter values are being written to persistent cookies, causing HTTP errors."
        elif risk_score >= 5:
            risk_level = 'Medium'
            vulnerability_type = 'Cookie Bomb (Potential)'
            summary = "Medium risk cookie bomb vulnerability. Parameter values are being written to cookies with potential for exploitation."
        elif risk_score >= 3:
            risk_level = 'Low'
            vulnerability_type = 'Cookie Writing'
            summary = "Low risk cookie writing detected. Parameter values are being written to cookies but no immediate exploitation path."
        else:
            risk_level = 'Info'
            vulnerability_type = 'No Vulnerability'
            summary = "No cookie bomb vulnerability detected."
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'vulnerability_type': vulnerability_type,
            'summary': summary
        }

    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        risk_level = analysis.get('risk_level', 'Low')
        
        if risk_level == 'High':
            recommendations.extend([
                "Immediately investigate and fix the cookie writing behavior",
                "Implement input validation and sanitization for URL parameters",
                "Set appropriate cookie size limits on the server",
                "Consider implementing rate limiting for cookie operations",
                "Review and update security headers configuration",
                "Test the fix thoroughly to ensure vulnerability is resolved"
            ])
        elif risk_level == 'Medium':
            recommendations.extend([
                "Review the cookie writing implementation",
                "Implement parameter validation to prevent excessive values",
                "Consider setting maximum cookie size limits",
                "Monitor for potential exploitation attempts",
                "Implement proper error handling for oversized requests"
            ])
        elif risk_level == 'Low':
            recommendations.extend([
                "Review cookie writing practices",
                "Consider implementing parameter validation",
                "Monitor for unusual cookie patterns",
                "Document the current behavior for future reference"
            ])
        else:
            recommendations.append("No immediate action required, but continue monitoring")
        
        return recommendations

    def analyze_multiple_results(self, results: List[Dict]) -> Dict:
        """Analyze multiple test results and provide aggregate analysis"""
        if not results:
            return {
                'total_tests': 0,
                'risk_distribution': {},
                'overall_risk': 'Info',
                'vulnerabilities_found': 0,
                'summary': 'No tests performed'
            }
        
        # Count risk levels
        risk_counts = {}
        vulnerabilities_found = 0
        
        for result in results:
            analysis = self.analyze_result(result)
            risk_level = analysis['risk_level']
            risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
            
            if risk_level in ['High', 'Medium']:
                vulnerabilities_found += 1
        
        # Determine overall risk
        if risk_counts.get('High', 0) > 0:
            overall_risk = 'High'
        elif risk_counts.get('Medium', 0) > 0:
            overall_risk = 'Medium'
        elif risk_counts.get('Low', 0) > 0:
            overall_risk = 'Low'
        else:
            overall_risk = 'Info'
        
        return {
            'total_tests': len(results),
            'risk_distribution': risk_counts,
            'overall_risk': overall_risk,
            'vulnerabilities_found': vulnerabilities_found,
            'summary': f"Found {vulnerabilities_found} potential vulnerabilities out of {len(results)} tests"
        }

    def generate_cvss_score(self, analysis: Dict) -> Dict:
        """Generate CVSS score for the vulnerability"""
        # Base CVSS metrics for cookie bomb vulnerability
        cvss_metrics = {
            'attack_vector': 'N',      # Network
            'attack_complexity': 'L',  # Low
            'privileges_required': 'N', # None
            'user_interaction': 'N',   # None
            'scope': 'U',              # Unchanged
            'confidentiality': 'N',    # None
            'integrity': 'L',          # Low
            'availability': 'H'        # High
        }
        
        # Adjust based on analysis
        if analysis.get('risk_level') == 'High':
            cvss_metrics['availability'] = 'H'  # High availability impact
        elif analysis.get('risk_level') == 'Medium':
            cvss_metrics['availability'] = 'M'  # Medium availability impact
        else:
            cvss_metrics['availability'] = 'L'  # Low availability impact
        
        # Calculate CVSS score
        cvss_score = self._calculate_cvss_score(cvss_metrics)
        
        return {
            'cvss_metrics': cvss_metrics,
            'cvss_score': cvss_score,
            'cvss_vector': f"CVSS:3.0/AV:{cvss_metrics['attack_vector']}/AC:{cvss_metrics['attack_complexity']}/PR:{cvss_metrics['privileges_required']}/UI:{cvss_metrics['user_interaction']}/S:{cvss_metrics['scope']}/C:{cvss_metrics['confidentiality']}/I:{cvss_metrics['integrity']}/A:{cvss_metrics['availability']}"
        }

    def _calculate_cvss_score(self, metrics: Dict) -> float:
        """Calculate CVSS score from metrics"""
        # Simplified CVSS calculation
        # In a real implementation, you would use the full CVSS formula
        
        base_scores = {
            'N': 0, 'L': 0.22, 'H': 0.56,  # Attack Vector
            'L': 0.77, 'H': 0.44,           # Attack Complexity
            'N': 0.85, 'L': 0.62, 'H': 0.27, # Privileges Required
            'N': 0.85, 'R': 0.62,           # User Interaction
            'U': 6.42, 'C': 7.52,           # Scope
            'N': 0, 'L': 0.22, 'H': 0.56,   # Confidentiality
            'N': 0, 'L': 0.22, 'H': 0.56,   # Integrity
            'N': 0, 'L': 0.22, 'H': 0.56    # Availability
        }
        
        # This is a simplified calculation
        # Real CVSS calculation is more complex
        score = 5.0  # Base score for cookie bomb
        
        if metrics['availability'] == 'H':
            score += 2.0
        elif metrics['availability'] == 'M':
            score += 1.0
        
        return min(10.0, max(0.0, score)) 