"""
Main Test Runner
Entry point for running the complete test suite

Usage:
    python main.py                          # Run all tests
    python main.py --integration            # Run only integration tests
    python main.py --e2e                    # Run only E2E tests
    python main.py --auth                   # Run only auth tests
    python main.py --quiz                   # Run only quiz tests
    python main.py --module <module_name>   # Run specific test module
    python main.py --parallel               # Run tests in parallel
    python main.py --html                   # Generate HTML report
"""

import sys
import os
import pytest
import argparse
from datetime import datetime
from colorama import init, Fore, Style
from test_config import config

# Initialize colorama for colored output
init(autoreset=True)


def print_banner():
    """Print test suite banner"""
    banner = f"""
{Fore.CYAN}{'='*70}
{Fore.CYAN}  Kambaz Backend API Test Suite
{Fore.CYAN}  Comprehensive Automated Testing
{Fore.CYAN}{'='*70}{Style.RESET_ALL}
"""
    print(banner)


def print_section(title):
    """Print section header"""
    print(f"\n{Fore.YELLOW}{'='*70}")
    print(f"{Fore.YELLOW}  {title}")
    print(f"{Fore.YELLOW}{'='*70}{Style.RESET_ALL}\n")


def get_test_modules():
    """Get list of available test modules"""
    modules = {
        "auth": "integration/test_auth.py",
        "users": "integration/test_users.py",
        "courses": "integration/test_courses.py",
        "enrollments": "integration/test_enrollments.py",
        "modules": "integration/test_modules.py",
        "assignments": "integration/test_assignments.py",
        "quizzes": "integration/test_quizzes.py",
        "quiz_attempts": "integration/test_quiz_attempts.py",
        "student_workflow": "e2e/test_student_workflow.py",
        "faculty_workflow": "e2e/test_faculty_workflow.py"
    }
    return modules


def run_tests(args):
    """
    Run tests based on command line arguments

    Args:
        args: Parsed command line arguments
    """
    print_banner()
    config.print_config()

    # Build pytest arguments
    pytest_args = config.PYTEST_ARGS.copy()

    # Add test selection based on arguments
    if args.module:
        modules = get_test_modules()
        if args.module in modules:
            pytest_args.append(modules[args.module])
            print_section(f"Running {args.module} tests")
        else:
            print(f"{Fore.RED}Error: Unknown module '{args.module}'")
            print(f"{Fore.YELLOW}Available modules: {', '.join(modules.keys())}")
            return 1
    elif args.integration:
        pytest_args.extend(["-m", "integration"])
        print_section("Running Integration Tests")
    elif args.e2e:
        pytest_args.extend(["-m", "e2e"])
        print_section("Running E2E Tests")
    elif args.auth:
        pytest_args.extend(["-m", "auth"])
        print_section("Running Authentication Tests")
    elif args.quiz:
        pytest_args.extend(["-m", "quiz"])
        print_section("Running Quiz Tests")
    else:
        print_section("Running All Tests")

    # Add parallel execution if requested
    if args.parallel or config.ENABLE_PARALLEL_TESTS:
        pytest_args.extend(["-n", str(config.PARALLEL_WORKERS)])
        print(f"{Fore.GREEN}Running tests in parallel with {config.PARALLEL_WORKERS} workers{Style.RESET_ALL}")

    # Add HTML report if requested
    if args.html or config.ENABLE_HTML_REPORT:
        report_path = os.path.join(os.path.dirname(__file__), config.HTML_REPORT_PATH)
        pytest_args.extend(["--html", report_path, "--self-contained-html"])
        print(f"{Fore.GREEN}HTML report will be generated at: {report_path}{Style.RESET_ALL}")

    # Add JSON report if requested
    if args.json or config.ENABLE_JSON_REPORT:
        report_path = os.path.join(os.path.dirname(__file__), config.JSON_REPORT_PATH)
        pytest_args.extend(["--json-report", f"--json-report-file={report_path}"])
        print(f"{Fore.GREEN}JSON report will be generated at: {report_path}{Style.RESET_ALL}")

    # Add verbose flag if requested
    if args.verbose:
        pytest_args.append("-vv")

    # Add quiet flag if requested
    if args.quiet:
        pytest_args.append("-q")

    # Add specific test path if provided
    if args.path:
        pytest_args.append(args.path)

    # Run pytest
    print(f"\n{Fore.CYAN}Starting test execution...{Style.RESET_ALL}\n")
    start_time = datetime.now()

    exit_code = pytest.main(pytest_args)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Print summary
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}  Test Execution Summary")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Exit Code: {exit_code}")

    if exit_code == 0:
        print(f"{Fore.GREEN}All tests passed!{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Some tests failed. Check the output above for details.{Style.RESET_ALL}")

    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

    return exit_code


def list_modules():
    """List all available test modules"""
    print_banner()
    print_section("Available Test Modules")

    modules = get_test_modules()
    print(f"{Fore.CYAN}Integration Tests:{Style.RESET_ALL}")
    for name, path in modules.items():
        if path.startswith("integration/"):
            print(f"  - {Fore.GREEN}{name}{Style.RESET_ALL}: {path}")

    print(f"\n{Fore.CYAN}E2E Tests:{Style.RESET_ALL}")
    for name, path in modules.items():
        if path.startswith("e2e/"):
            print(f"  - {Fore.GREEN}{name}{Style.RESET_ALL}: {path}")

    print(f"\n{Fore.YELLOW}Usage:{Style.RESET_ALL}")
    print(f"  python main.py --module {Fore.GREEN}<module_name>{Style.RESET_ALL}")
    print()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Kambaz Backend API Test Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                          # Run all tests
  python main.py --integration            # Run only integration tests
  python main.py --e2e                    # Run only E2E tests
  python main.py --module auth            # Run authentication tests
  python main.py --module quizzes         # Run quiz tests
  python main.py --parallel               # Run tests in parallel
  python main.py --html                   # Generate HTML report
  python main.py --list-modules           # List all available modules
  python main.py --path integration/      # Run all integration tests
        """
    )

    parser.add_argument(
        "--integration",
        action="store_true",
        help="Run only integration tests"
    )

    parser.add_argument(
        "--e2e",
        action="store_true",
        help="Run only E2E workflow tests"
    )

    parser.add_argument(
        "--auth",
        action="store_true",
        help="Run only authentication tests"
    )

    parser.add_argument(
        "--quiz",
        action="store_true",
        help="Run only quiz-related tests"
    )

    parser.add_argument(
        "--module",
        type=str,
        help="Run specific test module (e.g., auth, users, courses)"
    )

    parser.add_argument(
        "--path",
        type=str,
        help="Run tests at specific path (e.g., integration/test_auth.py)"
    )

    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run tests in parallel"
    )

    parser.add_argument(
        "--html",
        action="store_true",
        help="Generate HTML test report"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Generate JSON test report"
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output"
    )

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Quiet output"
    )

    parser.add_argument(
        "--list-modules",
        action="store_true",
        help="List all available test modules"
    )

    args = parser.parse_args()

    if args.list_modules:
        list_modules()
        return 0

    return run_tests(args)


if __name__ == "__main__":
    sys.exit(main())
