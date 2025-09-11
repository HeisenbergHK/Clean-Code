#!/usr/bin/env python3
"""
Test runner script for the FastAPI Affiliate Payout Management System.
Provides convenient commands for running different types of tests.
"""

import subprocess
import sys
import argparse


def run_command(command):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Exit code: {e.returncode}")
        print(f"Error output: {e.stderr}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Run tests for the FastAPI application")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Run tests in verbose mode")
    parser.add_argument("--file", type=str, help="Run specific test file")
    
    args = parser.parse_args()
    
    # Base pytest command
    base_cmd = "pytest"
    
    # Add verbose flag if requested
    if args.verbose:
        base_cmd += " -v"
    
    # Determine which tests to run
    if args.unit:
        cmd = f'{base_cmd} -m "not integration"'
        print("🧪 Running unit tests...")
    elif args.integration:
        cmd = f'{base_cmd} -m integration'
        print("🔗 Running integration tests...")
    elif args.file:
        cmd = f"{base_cmd} tests/{args.file}"
        print(f"📄 Running tests from {args.file}...")
    elif args.coverage:
        cmd = f"{base_cmd} --cov=app --cov-report=html --cov-report=term"
        print("📊 Running tests with coverage report...")
    else:
        cmd = base_cmd
        print("🚀 Running all tests...")
    
    # Run the tests
    success = run_command(cmd)
    
    if success:
        print("✅ Tests completed successfully!")
        if args.coverage:
            print("📊 Coverage report generated in htmlcov/index.html")
    else:
        print("❌ Tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()