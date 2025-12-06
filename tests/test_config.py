"""
Test Configuration
Contains all configuration settings for the test suite
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if exists
load_dotenv()

class TestConfig:
    """Test suite configuration"""

    # Backend API Configuration
    BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:4000")
    API_PREFIX = "/api"

    # Full API URL
    API_URL = f"{BASE_URL}{API_PREFIX}"

    # Database Configuration
    DB_CONNECTION_STRING = os.getenv(
        "TEST_DB_CONNECTION_STRING",
        "mongodb://127.0.0.1:27017/kambaz_test"
    )
    DB_NAME = "kambaz_test"

    # Test User Credentials
    DEFAULT_PASSWORD = "password123"

    # Test Timeouts (seconds)
    REQUEST_TIMEOUT = 30

    # Pytest Configuration
    PYTEST_ARGS = [
        "-v",  # Verbose output
        "--tb=short",  # Shorter traceback format
        "--strict-markers",  # Error on unknown markers
        "-ra",  # Show extra test summary info for all except passed
    ]

    # HTML Report Configuration
    HTML_REPORT_PATH = "test_report.html"
    JSON_REPORT_PATH = "test_report.json"

    # Parallel Execution
    PARALLEL_WORKERS = 4  # Number of parallel test workers

    # Test Data
    SAMPLE_USERS = {
        "admin": {
            "username": "test_admin",
            "password": DEFAULT_PASSWORD,
            "firstName": "Admin",
            "lastName": "User",
            "email": "admin@test.com",
            "role": "ADMIN"
        },
        "faculty": {
            "username": "test_faculty",
            "password": DEFAULT_PASSWORD,
            "firstName": "Faculty",
            "lastName": "User",
            "email": "faculty@test.com",
            "role": "FACULTY"
        },
        "student": {
            "username": "test_student",
            "password": DEFAULT_PASSWORD,
            "firstName": "Student",
            "lastName": "User",
            "email": "student@test.com",
            "role": "STUDENT"
        },
        "ta": {
            "username": "test_ta",
            "password": DEFAULT_PASSWORD,
            "firstName": "TA",
            "lastName": "User",
            "email": "ta@test.com",
            "role": "TA"
        }
    }

    # Feature Flags
    ENABLE_DB_CLEANUP = True  # Clean database before tests
    ENABLE_PARALLEL_TESTS = False  # Run tests in parallel
    ENABLE_HTML_REPORT = True  # Generate HTML report
    ENABLE_JSON_REPORT = True  # Generate JSON report

    @classmethod
    def get_api_url(cls, endpoint):
        """Get full API URL for an endpoint"""
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]
        return f"{cls.API_URL}/{endpoint}"

    @classmethod
    def print_config(cls):
        """Print current configuration"""
        print("\n" + "="*60)
        print("Test Configuration")
        print("="*60)
        print(f"Base URL: {cls.BASE_URL}")
        print(f"API URL: {cls.API_URL}")
        print(f"Database: {cls.DB_NAME}")
        print(f"Parallel Tests: {cls.ENABLE_PARALLEL_TESTS}")
        print(f"Workers: {cls.PARALLEL_WORKERS if cls.ENABLE_PARALLEL_TESTS else 1}")
        print(f"HTML Report: {cls.ENABLE_HTML_REPORT}")
        print(f"JSON Report: {cls.ENABLE_JSON_REPORT}")
        print("="*60 + "\n")


# Create global config instance
config = TestConfig()
