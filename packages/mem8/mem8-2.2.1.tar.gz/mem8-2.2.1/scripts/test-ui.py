#!/usr/bin/env python3
"""
Test UI launcher script for mem8 development.
Provides easy access to pytest visualization tools.
"""

import subprocess
import sys
import webbrowser
from pathlib import Path
import argparse
import time

def run_html_report():
    """Generate HTML report and open in browser."""
    print("Running tests with HTML report generation...")
    
    # Ensure reports directory exists
    Path("reports").mkdir(exist_ok=True)
    
    # Run pytest with HTML output
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "--html=reports/pytest_report.html",
        "--self-contained-html",
        "--cov=mem8",
        "--cov-report=html:reports/htmlcov",
        "--cov-report=term-missing",
    ])
    
    if result.returncode == 0:
        print("Tests completed successfully!")
    else:
        print("Some tests failed.")
    
    # Open reports in browser
    report_path = Path("reports/pytest_report.html").absolute()
    coverage_path = Path("reports/htmlcov/index.html").absolute()
    
    print(f"Opening test report: {report_path}")
    webbrowser.open(f"file://{report_path}")
    
    time.sleep(1)  # Brief delay
    
    print(f"Opening coverage report: {coverage_path}")
    webbrowser.open(f"file://{coverage_path}")

def run_basic_tests():
    """Run basic pytest with terminal output."""
    print("Running basic tests...")
    
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "-v",
    ])
    
    return result.returncode == 0

def run_watch_mode():
    """Run tests in watch mode with HTML updates."""
    print("Starting test watch mode...")
    print("Tests will re-run automatically when files change")
    
    try:
        # Use pytest-xdist for file watching
        subprocess.run([
            sys.executable, "-m", "ptw",
            "--",
            "--html=reports/pytest_report.html",
            "--self-contained-html"
        ])
    except KeyboardInterrupt:
        print("Watch mode stopped by user")

def main():
    parser = argparse.ArgumentParser(description="mem8 Test UI Tools")
    parser.add_argument(
        "mode",
        choices=["html", "basic", "watch"],
        help="Test visualization mode"
    )
    
    args = parser.parse_args()
    
    if args.mode == "html":
        run_html_report()
    elif args.mode == "basic":
        run_basic_tests()
    elif args.mode == "watch":
        run_watch_mode()

if __name__ == "__main__":
    main()