#!/usr/bin/env python3
"""
CLI Orchestrator - Main entry point for BeelzeCookie
Handles user input and coordinates all modules
"""

import argparse
import sys
import json
from pathlib import Path
from typing import List, Optional

try:
    from .recon import ReconModule
    from .payload_generator import PayloadGenerator
    from .request_engine import RequestEngine
    from .analyzer import Analyzer
    from .reporter import Reporter
except ImportError:
    # Fallback for when run as script
    from recon import ReconModule
    from payload_generator import PayloadGenerator
    from request_engine import RequestEngine
    from analyzer import Analyzer
    from reporter import Reporter


def print_banner():
    """Print ASCII art banner"""
    banner = """

****************************************************************************************************
*******************************************************************#********************************
*********************************************************##******#@*****%#******#*******************
**************************************************#****#%#*******#%@#************#%%#***************
*****************************************************#@#****#***###%@%**************%@%*************
****************************************************#@%**##@%%@%%##@@@#**#***********#@@%***********
***************************************************##@@###%#%%%%%#%@@@****************#@@%#*********
***************************************************#%#%%%%%%%%%%@@@@@@%#**************#@@@%#********
****************************************************#%%#%%%@@@@@@@@@@%%####************@@@@%#*******
****************************************************#@%%%@#**#@%%@@@@@#****************@@@@@%*******
*****************************************************#*%%@***#@@@@@@@@@##%#***********#@@@@@%%******
*****************************************************%%@@%@%%@@%@@@@@@@@%%###*********%@@@@@@%#*****
******************************************************%%%%%%#%%@%@@@@@@@@@%##********#@@@@@@@@@*****
*********#@@@@@%%%%%%%%%%%%%@#************************#%###%%@%@@@@@@@@@%@%@%#******#%@@@@@%@@%#****
*********%@@@@@@@@@@@@@@@@@@@%*************************%%%%%@@@@@@@@@@@%%%@@@%#*****%@@@@@@@@@%#****
*********%@@@@@@@@@@@@@@@@@@@%*******************************%@@@@@@@@%%#%%@@%#****%@@@@@@@@@@@%****
*********#@@@@@@@@@@@@@@@@@@@%*****************************#@@@@@@@@@%@%%%@@@%****%@#***@@@***@%****
*********#@@@@@@@@@@@@@@@@@@@%*****************************#@@@@@@%@@@%%%%@@@###*#@%****#%****#@****
*********#@@@@@@@@@@@@@@@@@@@%****************************#%@@@@@@@@@@%%%%@@@@%##@%*****%#****#@****
*********#@@@@@@@@@@@@@@@@@@@@***************************#%@@@@@@@@@@%%%%%@@@@#%#*******%*****#%****
*********#@@@@@@@@@@@@@@@@@@@@**************************%%@@@@%@@@@@@%%%%@@@@%%****************%****
*********#@@@@@@@@@@@@@@@@@@@@*********************##%%@%@@@%*#@@@@%#%%%@@@@@%#***************#%%***
*#**#*****##%%%@@@@@@@@@@@@@@@*************###%%%%@%@@@@@@@##%#%%%%%%%%@@@@@@%##*********###***#%***
##@@@@%%%#####@@@@@%#####%%%%#*###%%*****#@%@%%%%%%%%###%%#%%%%%%%%%%@@@@@@@@#*********%@%##%%##****
#%@@@@@@@%##@@@@@@@@@%%%#%@###%@@@@%%@@@@@@@@@@%@@@@%%%%%%%@%@@@@@@@@@@@@@@@@@@%%#%%%%%@#####@@%##**
%%@@%%@@@@%%@@@@@@@@@@@@@@%%%%%@@@@@@@@@@@@@@@@@@@@@@@@%%%%@@@@@@@@@@@@@@@@@@@@@%%%@%@%%%%%%%%@%####
@@@@@%%%%@%%%%%%%@@@@%@%%%%@%%@%%%%%#%%%%%@@%%@%%%%%%#%%%%%%%%@%%#%%%%%%@@%%@%@@@@@@@%@@@@@@@@@%%%%#
@@@@@@@@@@@@@@@@@@@@@%%%%%#%%%%#%%#%%@%%%#%#####%%###%%%%#%%%##%##@%#%#%%#%%%%@%@%#@@%@@@@%@@%%%%%%%
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%%%%%%%###%#######%%%###%%####%%####%%######%%#######%%%####%%#
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%@%%%%@%%%%%%%%%%%%%%%%%%%
                        ___  ____ ____ _    ___  ____ ____ ____ ____ _  _ _ ____
                        |__] |___ |___ |      /  |___ |    |  | |  | |_/  | |___
                        |__] |___ |___ |___  /__ |___ |___ |__| |__| | \_ | |___
    https://0xbthn.com
    https://github.com/0xbthn
    Maker: Batuhan Aydın

    I want to be a cookie.
    """
    print(banner)


class CLIOrchestrator:
    def __init__(self):
        self.recon = ReconModule()
        self.payload_gen = PayloadGenerator()
        self.request_engine = RequestEngine()
        self.analyzer = Analyzer()
        self.reporter = Reporter()

    def parse_arguments(self) -> argparse.Namespace:
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(
            description="BeelzeCookie - Cookie Bomb Vulnerability Scanner",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python -m beelzecookie --url https://example.com --auto --lengths 500,1000,2000
  python -m beelzecookie --urls targets.txt --params gclid,utm_source --lengths 1000,2000,4000
  python -m beelzecookie --url https://example.com --dry-run
  python -m beelzecookie --url https://example.com --live --proxy http://127.0.0.1:8080
            """
        )

        # URL input options
        url_group = parser.add_mutually_exclusive_group(required=True)
        url_group.add_argument(
            "--url",
            help="Single target URL to test"
        )
        url_group.add_argument(
            "--urls",
            help="File containing list of URLs to test (one per line)"
        )

        # Parameter options
        param_group = parser.add_mutually_exclusive_group(required=True)
        param_group.add_argument(
            "--params",
            help="Comma-separated list of parameters to test"
        )
        param_group.add_argument(
            "--auto",
            action="store_true",
            help="Automatically discover parameters using reconnaissance"
        )

        # Payload configuration
        parser.add_argument(
            "--lengths",
            default="500,1000,2000,4000",
            help="Comma-separated list of payload lengths to test (default: 500,1000,2000,4000)"
        )

        # Testing modes
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Only check for Set-Cookie headers, no exploitation"
        )

        parser.add_argument(
            "--live",
            action="store_true",
            help="Perform cookie persistence and error testing"
        )

        # Request configuration
        parser.add_argument(
            "--proxy",
            help="Proxy URL (e.g., http://127.0.0.1:8080 for Burp Suite)"
        )

        parser.add_argument(
            "--timeout",
            type=int,
            default=30,
            help="Request timeout in seconds (default: 30)"
        )

        parser.add_argument(
            "--delay",
            type=float,
            default=1.0,
            help="Delay between requests in seconds (default: 1.0)"
        )

        # Output options
        parser.add_argument(
            "--output",
            help="Output file for results (JSON format)"
        )

        parser.add_argument(
            "--report",
            help="Generate markdown report file"
        )

        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Enable verbose output"
        )

        return parser.parse_args()

    def load_urls(self, urls_arg: str) -> List[str]:
        """Load URLs from file or single URL"""
        if urls_arg.endswith('.txt') or Path(urls_arg).exists():
            with open(urls_arg, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        else:
            return [urls_arg]

    def parse_lengths(self, lengths_str: str) -> List[int]:
        """Parse payload lengths from comma-separated string"""
        try:
            return [int(x.strip()) for x in lengths_str.split(',')]
        except ValueError:
            print("Error: Invalid payload lengths format. Use comma-separated integers.")
            sys.exit(1)

    def parse_params(self, params_str: str) -> List[str]:
        """Parse parameters from comma-separated string"""
        return [x.strip() for x in params_str.split(',')]

    def run(self):
        """Main execution flow"""
        args = self.parse_arguments()

        # Load URLs
        urls = self.load_urls(args.url or args.urls)
        if not urls:
            print("Error: No valid URLs found")
            sys.exit(1)

        # Parse payload lengths
        payload_lengths = self.parse_lengths(args.lengths)

        # Parse parameters
        if args.params:
            parameters = self.parse_params(args.params)
        else:
            parameters = []

        # Configure request engine
        if args.proxy:
            self.request_engine.set_proxy(args.proxy)
        
        self.request_engine.set_timeout(args.timeout)
        self.request_engine.set_delay(args.delay)

        results = []

        for url in urls:
            print(f"\n[*] Testing URL: {url}")

            # Parameter discovery if auto mode
            if args.auto:
                print("[+] Discovering parameters automatically...")
                discovered_params = self.recon.discover_parameters(url)
                if discovered_params:
                    parameters = discovered_params
                    print(f"[+] Discovered parameters: {', '.join(parameters)}")
                else:
                    print("[-] No parameters discovered, using default list")
                    parameters = ['gclid', 'utm_source', 'utm_medium', 'utm_campaign', 'fbclid', 'dclid']

            if not parameters:
                print("[-] No parameters to test")
                continue

            # Test each parameter
            for param in parameters:
                print(f"\n[+] Testing parameter: {param}")

                # Generate payloads
                payloads = self.payload_gen.generate_payloads(param, payload_lengths)

                for payload_length, payload in payloads:
                    print(f"  [*] Testing payload length: {payload_length}")

                    if args.dry_run:
                        # Dry run mode - only check Set-Cookie
                        result = self.request_engine.dry_run_test(url, param, payload)
                    else:
                        # Full test mode
                        result = self.request_engine.full_test(url, param, payload, args.live)

                    # Analyze results
                    analysis = self.analyzer.analyze_result(result)
                    
                    result_data = {
                        'url': url,
                        'parameter': param,
                        'payload_length': payload_length,
                        'result': result,
                        'analysis': analysis
                    }
                    
                    results.append(result_data)

                    # Print immediate results
                    if args.verbose:
                        self._print_result(result_data)
                    else:
                        self._print_summary(result_data)

        # Generate reports
        if args.output:
            self.reporter.save_json(results, args.output)
            print(f"\n[+] Results saved to: {args.output}")

        if args.report:
            self.reporter.generate_markdown_report(results, args.report)
            print(f"[+] Report generated: {args.report}")

        # Print final summary
        self._print_final_summary(results)

    def _print_result(self, result_data: dict):
        """Print detailed result information"""
        analysis = result_data['analysis']
        print(f"    Risk Level: {analysis['risk_level']}")
        print(f"    Cookie Size Increase: {analysis.get('cookie_size_increase', 'N/A')}")
        print(f"    HTTP Status: {result_data['result'].get('second_status', 'N/A')}")
        print(f"    Cookie Persistence: {analysis.get('cookie_persistence', 'N/A')}")

    def _print_summary(self, result_data: dict):
        """Print summary of result"""
        analysis = result_data['analysis']
        risk_emoji = {
            'High': '🔴',
            'Medium': '🟡', 
            'Low': '🟢'
        }
        print(f"    {risk_emoji.get(analysis['risk_level'], '⚪')} {analysis['risk_level']} - {analysis['summary']}")

    def _print_final_summary(self, results: List[dict]):
        """Print final summary of all tests"""
        print(f"\n{'='*60}")
        print("FINAL SUMMARY")
        print(f"{'='*60}")
        
        high_count = sum(1 for r in results if r['analysis']['risk_level'] == 'High')
        medium_count = sum(1 for r in results if r['analysis']['risk_level'] == 'Medium')
        low_count = sum(1 for r in results if r['analysis']['risk_level'] == 'Low')
        
        print(f"🔴 High Risk Findings: {high_count}")
        print(f"🟡 Medium Risk Findings: {medium_count}")
        print(f"🟢 Low Risk Findings: {low_count}")
        print(f"📊 Total Tests: {len(results)}")
        
        if high_count > 0:
            print(f"\n🚨 Cookie Bomb vulnerabilities detected! Check the detailed results.")


def main():
    """Main entry point"""
    print_banner()
    orchestrator = CLIOrchestrator()
    try:
        orchestrator.run()
    except KeyboardInterrupt:
        print("\n[!] Scan interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[!] Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 