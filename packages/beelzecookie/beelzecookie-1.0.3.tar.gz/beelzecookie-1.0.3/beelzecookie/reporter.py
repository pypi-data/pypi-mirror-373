"""
Reporter Module - Report Generation
Generates JSON and Markdown reports for bug bounty submissions
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class Reporter:
    def __init__(self):
        self.report_template = {
            'scan_info': {},
            'targets': [],
            'findings': [],
            'summary': {},
            'timestamp': ''
        }

    def save_json(self, results: List[Dict], output_file: str):
        """Save results to JSON file"""
        try:
            # Prepare the report structure
            report = {
                'scan_info': {
                    'tool': 'BeelzeCookie',
                    'version': '1.0.0',
                    'timestamp': datetime.now().isoformat(),
                    'total_tests': len(results)
                },
                'targets': self._extract_targets(results),
                'findings': self._prepare_findings(results),
                'summary': self._generate_summary(results)
            }
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
            
            # Write JSON file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error saving JSON report: {e}")

    def generate_markdown_report(self, results: List[Dict], output_file: str):
        """Generate Markdown report for bug bounty submission"""
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(self._generate_markdown_content(results))
                
        except Exception as e:
            print(f"Error generating Markdown report: {e}")

    def _extract_targets(self, results: List[Dict]) -> List[Dict]:
        """Extract unique targets from results"""
        targets = {}
        
        for result in results:
            url = result.get('url', '')
            if url not in targets:
                targets[url] = {
                    'url': url,
                    'parameters_tested': [],
                    'findings_count': 0
                }
            
            param = result.get('parameter', '')
            if param not in targets[url]['parameters_tested']:
                targets[url]['parameters_tested'].append(param)
            
            # Count findings
            analysis = result.get('analysis', {})
            if analysis.get('risk_level') in ['High', 'Medium']:
                targets[url]['findings_count'] += 1
        
        return list(targets.values())

    def _prepare_findings(self, results: List[Dict]) -> List[Dict]:
        """Prepare findings for JSON output"""
        findings = []
        
        for result in results:
            analysis = result.get('analysis', {})
            
            # Only include findings with risk
            if analysis.get('risk_level') in ['High', 'Medium', 'Low']:
                finding = {
                    'url': result.get('url', ''),
                    'parameter': result.get('parameter', ''),
                    'payload_length': result.get('payload_length', 0),
                    'risk_level': analysis.get('risk_level', 'Info'),
                    'vulnerability_type': analysis.get('vulnerability_type', ''),
                    'summary': analysis.get('summary', ''),
                    'risk_factors': analysis.get('risk_factors', []),
                    'cookie_size_increase': analysis.get('cookie_size_increase', 0),
                    'cookie_persistence': analysis.get('cookie_persistence', False),
                    'error_detected': analysis.get('error_detected', False),
                    'first_status': result.get('result', {}).get('first_status'),
                    'second_status': result.get('result', {}).get('second_status'),
                    'recommendations': analysis.get('recommendations', [])
                }
                findings.append(finding)
        
        return findings

    def _generate_summary(self, results: List[Dict]) -> Dict:
        """Generate summary statistics"""
        total_tests = len(results)
        risk_counts = {'High': 0, 'Medium': 0, 'Low': 0, 'Info': 0}
        
        for result in results:
            analysis = result.get('analysis', {})
            risk_level = analysis.get('risk_level', 'Info')
            risk_counts[risk_level] += 1
        
        vulnerabilities_found = risk_counts['High'] + risk_counts['Medium']
        
        return {
            'total_tests': total_tests,
            'vulnerabilities_found': vulnerabilities_found,
            'risk_distribution': risk_counts,
            'overall_risk': 'High' if risk_counts['High'] > 0 else 'Medium' if risk_counts['Medium'] > 0 else 'Low' if risk_counts['Low'] > 0 else 'Info'
        }

    def _generate_markdown_content(self, results: List[Dict]) -> str:
        """Generate Markdown content for the report"""
        content = []
        
        # Header
        content.append("# Cookie Bomb Vulnerability Scan Report")
        content.append("")
        content.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append(f"**Tool:** BeelzeCookie v1.0.0")
        content.append("")
        
        # Executive Summary
        content.append("## Executive Summary")
        content.append("")
        
        summary = self._generate_summary(results)
        content.append(f"This scan tested **{summary['total_tests']}** parameter combinations across the target application(s).")
        content.append(f"**{summary['vulnerabilities_found']}** potential cookie bomb vulnerabilities were identified.")
        content.append("")
        
        # Risk Distribution
        content.append("### Risk Distribution")
        content.append("")
        for risk_level, count in summary['risk_distribution'].items():
            if count > 0:
                emoji = {'High': '🔴', 'Medium': '🟡', 'Low': '🟢', 'Info': '⚪'}.get(risk_level, '⚪')
                content.append(f"- {emoji} **{risk_level}:** {count} findings")
        content.append("")
        
        # High Risk Findings
        high_risk_findings = [r for r in results if r.get('analysis', {}).get('risk_level') == 'High']
        if high_risk_findings:
            content.append("## 🔴 High Risk Findings")
            content.append("")
            
            for i, finding in enumerate(high_risk_findings, 1):
                content.extend(self._format_finding_markdown(finding, i, 'High'))
                content.append("")
        
        # Medium Risk Findings
        medium_risk_findings = [r for r in results if r.get('analysis', {}).get('risk_level') == 'Medium']
        if medium_risk_findings:
            content.append("## 🟡 Medium Risk Findings")
            content.append("")
            
            for i, finding in enumerate(medium_risk_findings, 1):
                content.extend(self._format_finding_markdown(finding, i, 'Medium'))
                content.append("")
        
        # Low Risk Findings
        low_risk_findings = [r for r in results if r.get('analysis', {}).get('risk_level') == 'Low']
        if low_risk_findings:
            content.append("## 🟢 Low Risk Findings")
            content.append("")
            
            for i, finding in enumerate(low_risk_findings, 1):
                content.extend(self._format_finding_markdown(finding, i, 'Low'))
                content.append("")
        
        # Methodology
        content.append("## Methodology")
        content.append("")
        content.append("This scan was performed using the following methodology:")
        content.append("")
        content.append("1. **Parameter Discovery:** Automated discovery of URL parameters using HTML/JS parsing")
        content.append("2. **Payload Generation:** Creation of various payload sizes and types for each parameter")
        content.append("3. **Cookie Analysis:** Monitoring Set-Cookie headers and cookie persistence")
        content.append("4. **Error Detection:** Analysis of HTTP status codes for DoS indicators")
        content.append("5. **Risk Assessment:** Comprehensive scoring based on multiple factors")
        content.append("")
        
        # Recommendations
        content.append("## Recommendations")
        content.append("")
        content.append("### Immediate Actions")
        content.append("- Implement input validation for URL parameters")
        content.append("- Set appropriate cookie size limits on the server")
        content.append("- Review and update security headers configuration")
        content.append("")
        
        content.append("### Long-term Improvements")
        content.append("- Implement rate limiting for cookie operations")
        content.append("- Add monitoring for unusual cookie patterns")
        content.append("- Regular security testing and vulnerability assessments")
        content.append("")
        
        # Technical Details
        content.append("## Technical Details")
        content.append("")
        content.append("### Tested Parameters")
        tested_params = set()
        for result in results:
            tested_params.add(result.get('parameter', ''))
        
        content.append("The following parameters were tested:")
        content.append("")
        for param in sorted(tested_params):
            content.append(f"- `{param}`")
        content.append("")
        
        content.append("### Payload Sizes")
        content.append("Payloads of various sizes were tested to identify the threshold at which cookie bomb vulnerabilities manifest.")
        content.append("")
        
        # Footer
        content.append("---")
        content.append("*This report was generated automatically by BeelzeCookie. For questions or support, please refer to the tool documentation.*")
        
        return "\n".join(content)

    def _format_finding_markdown(self, result: Dict, finding_number: int, risk_level: str) -> List[str]:
        """Format a single finding for Markdown"""
        content = []
        analysis = result.get('analysis', {})
        
        # Finding header
        content.append(f"### Finding #{finding_number}: {analysis.get('vulnerability_type', 'Cookie Bomb Vulnerability')}")
        content.append("")
        
        # Basic information
        content.append("**Target URL:**")
        content.append(f"```")
        content.append(result.get('url', ''))
        content.append(f"```")
        content.append("")
        
        content.append("**Parameter:** `" + result.get('parameter', '') + "`")
        content.append("")
        
        content.append("**Payload Length:** " + str(result.get('payload_length', 0)) + " characters")
        content.append("")
        
        # Summary
        content.append("**Summary:**")
        content.append(analysis.get('summary', ''))
        content.append("")
        
        # Risk factors
        risk_factors = analysis.get('risk_factors', [])
        if risk_factors:
            content.append("**Risk Factors:**")
            for factor in risk_factors:
                content.append(f"- {factor}")
            content.append("")
        
        # Technical details
        content.append("**Technical Details:**")
        content.append("")
        
        result_data = result.get('result', {})
        
        # HTTP status codes
        first_status = result_data.get('first_status')
        second_status = result_data.get('second_status')
        if first_status or second_status:
            content.append("- **HTTP Status Codes:**")
            if first_status:
                content.append(f"  - First request: {first_status}")
            if second_status:
                content.append(f"  - Second request: {second_status}")
            content.append("")
        
        # Cookie information
        cookie_size_increase = analysis.get('cookie_size_increase', 0)
        if cookie_size_increase > 0:
            content.append(f"- **Cookie Size Increase:** {cookie_size_increase} bytes")
            content.append("")
        
        cookie_persistence = analysis.get('cookie_persistence', False)
        if cookie_persistence:
            content.append("- **Cookie Persistence:** Yes (cookies persist across requests)")
            content.append("")
        
        # Recommendations
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            content.append("**Recommendations:**")
            for rec in recommendations:
                content.append(f"- {rec}")
            content.append("")
        
        # Proof of Concept
        if risk_level in ['High', 'Medium']:
            content.append("**Proof of Concept:**")
            content.append("")
            content.append("To reproduce this vulnerability:")
            content.append("")
            content.append("1. Visit the target URL with a large payload in the vulnerable parameter")
            content.append("2. Observe that cookies are set with the parameter value")
            content.append("3. Make subsequent requests to see if the cookies persist")
            content.append("4. Check for HTTP errors that indicate DoS conditions")
            content.append("")
            
            # Example URL
            content.append("**Example URL:**")
            content.append("```")
            content.append(result.get('url', ''))
            content.append("```")
            content.append("")
        
        return content

    def generate_hackerone_report(self, results: List[Dict]) -> str:
        """Generate a report specifically formatted for HackerOne submission"""
        content = []
        
        # Find the highest risk finding
        high_risk_findings = [r for r in results if r.get('analysis', {}).get('risk_level') == 'High']
        if not high_risk_findings:
            medium_risk_findings = [r for r in results if r.get('analysis', {}).get('risk_level') == 'Medium']
            if not medium_risk_findings:
                return "No significant vulnerabilities found for HackerOne report."
            
            primary_finding = medium_risk_findings[0]
        else:
            primary_finding = high_risk_findings[0]
        
        analysis = primary_finding.get('analysis', {})
        
        # HackerOne format
        content.append("# Cookie Bomb Vulnerability")
        content.append("")
        
        content.append("## Summary")
        content.append(analysis.get('summary', ''))
        content.append("")
        
        content.append("## Steps To Reproduce")
        content.append("")
        content.append("1. Visit the target URL with a large payload in the vulnerable parameter")
        content.append("2. Observe that cookies are set with the parameter value")
        content.append("3. Make subsequent requests to see if the cookies persist")
        content.append("4. Check for HTTP errors that indicate DoS conditions")
        content.append("")
        
        content.append("## Impact")
        content.append("")
        content.append("This vulnerability can lead to:")
        content.append("- Denial of Service (DoS) attacks")
        content.append("- User account lockouts")
        content.append("- Increased server load")
        content.append("- Potential for persistent DoS conditions")
        content.append("")
        
        content.append("## Proof of Concept")
        content.append("")
        content.append("**Target URL:**")
        content.append(f"`{primary_finding.get('url', '')}`")
        content.append("")
        
        content.append("**Vulnerable Parameter:**")
        content.append(f"`{primary_finding.get('parameter', '')}`")
        content.append("")
        
        content.append("**Payload Size:**")
        content.append(f"`{primary_finding.get('payload_length', 0)}` characters")
        content.append("")
        
        # Add technical details
        result_data = primary_finding.get('result', {})
        first_status = result_data.get('first_status')
        second_status = result_data.get('second_status')
        
        if first_status or second_status:
            content.append("**HTTP Status Codes:**")
            if first_status:
                content.append(f"- First request: {first_status}")
            if second_status:
                content.append(f"- Second request: {second_status}")
            content.append("")
        
        return "\n".join(content) 