# BeelzeCookie - Cookie Bomb Vulnerability Scanner

![BeelzeCookie Logo](image.png)


A comprehensive tool for detecting cookie bomb vulnerabilities in web applications. Cookie bombs occur when URL parameters are directly written to cookies, allowing attackers to create oversized cookies that can cause Denial of Service (DoS) conditions.

## Features

- **Automated Parameter Discovery**: Automatically discovers URL parameters using HTML/JS parsing
- **Smart Payload Generation**: Creates realistic tracking-like payloads for testing
- **Cookie Analysis**: Monitors Set-Cookie headers and cookie persistence
- **Risk Assessment**: Comprehensive scoring based on multiple factors
- **Proxy Support**: Integrates with Burp Suite and other proxies
- **Rate Limiting**: Built-in throttling to avoid overwhelming targets
- **Multiple Output Formats**: JSON and Markdown reports for bug bounty submissions

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Install Dependencies

```bash
cd beelzecookie
pip install -r requirements.txt
```
### Setup.py install
```bash

cd beelzecookie

cp *.py beelzecookie_pkg/beelzecookie/

cp __init__.py beelzecookie_pkg/beelzecookie/

cp setup.py requirements.txt README.md beelzecookie_pkg/

cd beelzecookie_pkg

pip3 install -e . --break-system-packages

beelzecookie --help
```

## Usage

### Basic Usage

```bash
# Test a single URL with automatic parameter discovery
python main.py --url https://example.com --auto --lengths 500,1000,2000

# Test specific parameters
python main.py --url https://example.com --params gclid,utm_source,utm_medium --lengths 1000,2000,4000

# Test multiple URLs from a file
python main.py --urls targets.txt --auto --lengths 500,1000,2000

# Dry run mode (only check Set-Cookie headers)
python main.py --url https://example.com --dry-run

# Live testing with cookie persistence verification
python main.py --url https://example.com --live --proxy http://127.0.0.1:8080
```

### Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--url` | Single target URL | `--url https://example.com` |
| `--urls` | File containing URLs (one per line) | `--urls targets.txt` |
| `--params` | Comma-separated list of parameters to test | `--params gclid,utm_source` |
| `--auto` | Automatically discover parameters | `--auto` |
| `--lengths` | Payload lengths to test | `--lengths 500,1000,2000,4000` |
| `--dry-run` | Only check Set-Cookie headers | `--dry-run` |
| `--live` | Test cookie persistence and errors | `--live` |
| `--proxy` | Proxy URL for requests | `--proxy http://127.0.0.1:8080` |
| `--timeout` | Request timeout in seconds | `--timeout 30` |
| `--delay` | Delay between requests | `--delay 1.0` |
| `--output` | Save results to JSON file | `--output results.json` |
| `--report` | Generate Markdown report | `--report report.md` |
| `--verbose` | Enable verbose output | `--verbose` |

### Examples

#### 1. Basic Scan
```bash
python main.py --url https://example.com --auto --lengths 1000,2000
```

#### 2. Targeted Parameter Testing
```bash
python main.py --url https://example.com --params gclid,fbclid,utm_source --lengths 500,1000,2000,4000
```

#### 3. Multiple Target Scan
```bash
# Create targets.txt file
echo "https://example1.com" > targets.txt
echo "https://example2.com" >> targets.txt

# Run scan
python main.py --urls targets.txt --auto --lengths 1000,2000 --output results.json --report report.md
```

#### 4. Burp Suite Integration
```bash
python main.py --url https://example.com --live --proxy http://127.0.0.1:8080 --verbose
```

#### 5. Dry Run for Reconnaissance
```bash
python main.py --url https://example.com --dry-run --auto --verbose
```

## Output Formats

### Console Output
The tool provides real-time feedback with color-coded risk levels:
- 🔴 **High Risk**: Cookie bomb vulnerability detected
- 🟡 **Medium Risk**: Potential vulnerability with some risk factors
- 🟢 **Low Risk**: Cookie writing detected but no immediate threat
- ⚪ **Info**: No vulnerability detected

### JSON Report
Detailed results in JSON format for further processing:
```json
{
  "scan_info": {
    "tool": "BeelzeCookie",
    "version": "1.0.0",
    "timestamp": "2025-01-01T12:00:00",
    "total_tests": 24
  },
  "targets": [...],
  "findings": [...],
  "summary": {
    "total_tests": 24,
    "vulnerabilities_found": 3,
    "risk_distribution": {
      "High": 1,
      "Medium": 2,
      "Low": 5,
      "Info": 16
    }
  }
}
```

### Markdown Report
Professional report ready for bug bounty submission:
- Executive summary
- Detailed findings with risk levels
- Technical details and proof of concept
- Recommendations for remediation

## Risk Assessment

The tool evaluates vulnerabilities based on multiple factors:

### Risk Factors
1. **Cookie Writing**: Are cookies being set?
2. **Parameter Cookies**: Are parameter values written to cookies?
3. **Cookie Persistence**: Do cookies persist across requests?
4. **Error Detection**: Are HTTP errors occurring?
5. **Cookie Size**: How much do cookies increase in size?
6. **Status Transitions**: Do successful requests lead to errors?

### Risk Levels
- **High Risk (8+ points)**: Confirmed cookie bomb vulnerability
- **Medium Risk (5-7 points)**: Potential vulnerability with exploitation path
- **Low Risk (3-4 points)**: Cookie writing detected but limited impact
- **Info (0-2 points)**: No significant vulnerability

## Methodology

1. **Parameter Discovery**: 
   - Extract parameters from URL
   - Parse HTML forms and links
   - Analyze JavaScript files
   - Check for common tracking parameters

2. **Payload Generation**:
   - Create realistic tracking-like payloads
   - Generate various payload sizes
   - Test different encoding methods
   - Create combination payloads

3. **Cookie Analysis**:
   - Monitor Set-Cookie headers
   - Track cookie persistence
   - Measure cookie size changes
   - Analyze cookie content

4. **Error Detection**:
   - Monitor HTTP status codes
   - Detect DoS indicators (400, 413, 414, 431)
   - Analyze response patterns
   - Track request failures

5. **Risk Assessment**:
   - Score based on multiple factors
   - Calculate CVSS scores
   - Generate recommendations
   - Provide remediation guidance

## Common Vulnerable Parameters

The tool automatically tests these commonly vulnerable parameters:

### Tracking Parameters
- `gclid` (Google Click ID)
- `fbclid` (Facebook Click ID)
- `dclid` (DoubleClick ID)
- `msclkid` (Microsoft Click ID)

### UTM Parameters
- `utm_source`
- `utm_medium`
- `utm_campaign`
- `utm_term`
- `utm_content`

### Other Common Parameters
- `ref`, `source`, `campaign`
- `affiliate`, `partner`
- `tracking`, `track`
- `session`, `user`, `visitor`

## Security Considerations

### Responsible Disclosure
- Always obtain proper authorization before testing
- Follow responsible disclosure practices
- Respect rate limits and server resources
- Do not perform DoS attacks on production systems

### Legal Compliance
- Ensure you have permission to test the target
- Comply with applicable laws and regulations
- Follow bug bounty program guidelines
- Respect terms of service

## Troubleshooting

### Common Issues

1. **Connection Errors**
   - Check network connectivity
   - Verify target URL is accessible
   - Adjust timeout settings

2. **Proxy Issues**
   - Ensure proxy is running and accessible
   - Check proxy configuration
   - Verify certificate handling

3. **Rate Limiting**
   - Increase delay between requests
   - Use proxy to distribute requests
   - Respect server rate limits

4. **False Positives**
   - Review cookie analysis results
   - Check for legitimate cookie usage
   - Verify error conditions

### Debug Mode
Enable verbose output for detailed debugging:
```bash
python main.py --url https://example.com --verbose --auto
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

### Development Setup
```bash
git clone <repository>
cd beelzecookie
pip install -r requirements.txt
python main.py --help
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and authorized security testing purposes only. Users are responsible for ensuring they have proper authorization before testing any systems. The authors are not responsible for any misuse of this tool.

## Support

For support, questions, or bug reports:
- Open an issue on GitHub
- Check the documentation
- Review the troubleshooting section

---

**BeelzeCookie** - Making cookie bomb detection easier and more comprehensive. 