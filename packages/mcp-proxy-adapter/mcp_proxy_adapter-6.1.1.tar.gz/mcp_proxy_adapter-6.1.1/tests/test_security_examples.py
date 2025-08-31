"""
Security examples tester for MCP Proxy Adapter.

This module provides functionality to test all security examples
and save results for analysis.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from .clients.security_test_client import SecurityTestClient
from mcp_proxy_adapter.examples.security_configurations import TestConfigurationExamples


class SecurityExampleTester:
    """
    Tester for security examples.
    
    This class provides methods to run security tests using the SecurityTestClient
    and save results for analysis.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", results_dir: str = "test_results"):
        """
        Initialize the security example tester.
        
        Args:
            base_url: Base URL of the MCP Proxy Adapter
            results_dir: Directory to save test results
        """
        self.base_url = base_url
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        
    async def run_single_test(
        self, 
        test_config: Dict[str, Any],
        save_results: bool = True
    ) -> Dict[str, Any]:
        """
        Run a single security test.
        
        Args:
            test_config: Test configuration
            save_results: Whether to save results to file
            
        Returns:
            Test results
        """
        test_name = test_config.get("name", "unknown_test")
        print(f"Running test: {test_name}")
        
        try:
            async with SecurityTestClient(self.base_url) as client:
                results = await client.run_comprehensive_test(test_config)
                
                if save_results:
                    await self._save_test_results(test_name, results)
                
                print(f"Test {test_name} completed successfully")
                return results
                
        except Exception as e:
            error_result = {
                "test_name": test_name,
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
                "success": False
            }
            
            if save_results:
                await self._save_test_results(test_name, error_result)
            
            print(f"Test {test_name} failed: {e}")
            return error_result
    
    async def run_all_tests(
        self, 
        save_results: bool = True,
        parallel: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Run all security tests.
        
        Args:
            save_results: Whether to save results to files
            parallel: Whether to run tests in parallel
            
        Returns:
            List of test results
        """
        test_configs = TestConfigurationExamples.all_test_configs()
        print(f"Running {len(test_configs)} security tests...")
        
        if parallel:
            # Run tests in parallel
            tasks = [
                self.run_single_test(config, save_results=False)
                for config in test_configs
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Save results after parallel execution
            if save_results:
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        test_name = test_configs[i].get("name", f"test_{i}")
                        error_result = {
                            "test_name": test_name,
                            "timestamp": datetime.utcnow().isoformat(),
                            "error": str(result),
                            "success": False
                        }
                        await self._save_test_results(test_name, error_result)
                    else:
                        test_name = result.get("test_name", f"test_{i}")
                        await self._save_test_results(test_name, result)
        else:
            # Run tests sequentially
            results = []
            for config in test_configs:
                result = await self.run_single_test(config, save_results)
                results.append(result)
        
        return results
    
    async def run_specific_tests(
        self, 
        test_names: List[str],
        save_results: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Run specific security tests by name.
        
        Args:
            test_names: List of test names to run
            save_results: Whether to save results to files
            
        Returns:
            List of test results
        """
        all_configs = TestConfigurationExamples.all_test_configs()
        config_map = {config["name"]: config for config in all_configs}
        
        results = []
        for test_name in test_names:
            if test_name in config_map:
                result = await self.run_single_test(config_map[test_name], save_results)
                results.append(result)
            else:
                print(f"Test '{test_name}' not found")
                error_result = {
                    "test_name": test_name,
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": f"Test '{test_name}' not found",
                    "success": False
                }
                results.append(error_result)
        
        return results
    
    async def _save_test_results(self, test_name: str, results: Dict[str, Any]) -> None:
        """
        Save test results to file.
        
        Args:
            test_name: Name of the test
            results: Test results to save
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{test_name}_{timestamp}.json"
        filepath = self.results_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"Results saved to: {filepath}")
        except Exception as e:
            print(f"Failed to save results for {test_name}: {e}")
    
    async def generate_test_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a comprehensive test report.
        
        Args:
            results: List of test results
            
        Returns:
            Test report
        """
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_tests": len(results),
            "successful_tests": 0,
            "failed_tests": 0,
            "test_summary": {},
            "overall_success": True
        }
        
        for result in results:
            test_name = result.get("test_name", "unknown")
            success = result.get("success", False)
            
            if success:
                report["successful_tests"] += 1
            else:
                report["failed_tests"] += 1
                report["overall_success"] = False
            
            # Extract test details
            test_summary = {
                "success": success,
                "timestamp": result.get("timestamp"),
                "error": result.get("error")
            }
            
            # Add test-specific details
            if "tests" in result:
                test_summary["test_details"] = {}
                for test_type, test_result in result["tests"].items():
                    test_summary["test_details"][test_type] = {
                        "success": test_result.get("success", False),
                        "status_code": test_result.get("status_code")
                    }
            
            report["test_summary"][test_name] = test_summary
        
        return report
    
    async def save_test_report(self, report: Dict[str, Any]) -> None:
        """
        Save test report to file.
        
        Args:
            report: Test report to save
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"security_test_report_{timestamp}.json"
        filepath = self.results_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"Test report saved to: {filepath}")
        except Exception as e:
            print(f"Failed to save test report: {e}")


async def main():
    """Main function to run security tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run MCP Proxy Adapter security tests")
    parser.add_argument("--base-url", default="http://localhost:8000", 
                       help="Base URL of the MCP Proxy Adapter")
    parser.add_argument("--results-dir", default="test_results",
                       help="Directory to save test results")
    parser.add_argument("--parallel", action="store_true",
                       help="Run tests in parallel")
    parser.add_argument("--tests", nargs="+",
                       help="Specific tests to run")
    parser.add_argument("--no-save", action="store_true",
                       help="Don't save results to files")
    
    args = parser.parse_args()
    
    tester = SecurityExampleTester(args.base_url, args.results_dir)
    
    if args.tests:
        print(f"Running specific tests: {args.tests}")
        results = await tester.run_specific_tests(args.tests, not args.no_save)
    else:
        print("Running all security tests...")
        results = await tester.run_all_tests(not args.no_save, args.parallel)
    
    # Generate and save report
    report = await tester.generate_test_report(results)
    await tester.save_test_report(report)
    
    # Print summary
    print("\n" + "="*50)
    print("SECURITY TEST SUMMARY")
    print("="*50)
    print(f"Total tests: {report['total_tests']}")
    print(f"Successful: {report['successful_tests']}")
    print(f"Failed: {report['failed_tests']}")
    print(f"Overall success: {report['overall_success']}")
    
    if not report['overall_success']:
        print("\nFailed tests:")
        for test_name, summary in report['test_summary'].items():
            if not summary['success']:
                print(f"  - {test_name}: {summary.get('error', 'Unknown error')}")
    
    return 0 if report['overall_success'] else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
