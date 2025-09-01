#!/usr/bin/env python3
"""Test runner script for novus-pytils.

This script provides a convenient way to run different types of tests
with various options and configurations.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and handle the result."""
    if description:
        print(f"\n🚀 {description}")
    print(f"Running: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"✅ {description or 'Command'} completed successfully")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ {description or 'Command'} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        print("Make sure pytest is installed: pip install pytest")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Run tests for novus-pytils",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Run all tests
  %(prog)s --module utils           # Run utils module tests
  %(prog)s --coverage               # Run with coverage report
  %(prog)s --fast                   # Skip slow tests
  %(prog)s --verbose                # Verbose output
  %(prog)s --file test_validation   # Run specific test file
        """
    )
    
    parser.add_argument(
        "--module", "-m",
        choices=["utils", "types", "files", "compression", "text", "audio", "image", "video"],
        help="Run tests for specific module"
    )
    
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="Run tests with coverage report"
    )
    
    parser.add_argument(
        "--fast", "-f",
        action="store_true", 
        help="Skip slow tests"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose test output"
    )
    
    parser.add_argument(
        "--file", 
        help="Run specific test file (without .py extension)"
    )
    
    parser.add_argument(
        "--markers", 
        help="Run tests with specific markers (e.g., 'not slow')"
    )
    
    parser.add_argument(
        "--parallel", "-p",
        action="store_true",
        help="Run tests in parallel (requires pytest-xdist)"
    )
    
    args = parser.parse_args()
    
    # Build pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test path
    if args.module:
        cmd.append(f"tests/unit/{args.module}/")
    elif args.file:
        # Handle both with and without .py extension
        file_name = args.file
        if not file_name.endswith('.py'):
            file_name += '.py'
        if not file_name.startswith('test_'):
            file_name = f'test_{file_name}'
        cmd.append(f"tests/unit/*/{file_name}")
    else:
        cmd.append("tests/")
    
    # Add options
    if args.coverage:
        cmd.extend(["--cov=novus_pytils", "--cov-report=html", "--cov-report=term"])
    
    if args.verbose:
        cmd.append("-v")
    
    if args.fast:
        cmd.extend(["-m", "not slow"])
    
    if args.markers:
        cmd.extend(["-m", args.markers])
    
    if args.parallel:
        cmd.extend(["-n", "auto"])
    
    # Add some default useful options
    cmd.extend(["--tb=short", "--strict-markers"])
    
    # Determine description
    if args.module:
        description = f"Running {args.module} module tests"
    elif args.file:
        description = f"Running tests for {args.file}"
    else:
        description = "Running all tests"
    
    if args.coverage:
        description += " with coverage"
    if args.fast:
        description += " (fast mode)"
    
    # Run the tests
    success = run_command(cmd, description)
    
    if args.coverage and success:
        print(f"\n📊 Coverage report generated in htmlcov/index.html")
    
    # Print summary
    print("\n" + "="*50)
    if success:
        print("🎉 All tests completed successfully!")
    else:
        print("💥 Some tests failed. Check output above for details.")
        sys.exit(1)


if __name__ == "__main__":
    # Check if we're in the right directory
    if not Path("src/novus_pytils").exists():
        print("❌ Error: Run this script from the project root directory")
        print("   (where src/novus_pytils exists)")
        sys.exit(1)
    
    main()