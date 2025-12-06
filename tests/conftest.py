"""
Pytest Configuration
Defines fixtures and hooks for the test suite
"""

import pytest
import sys
import os

# Add parent directory to path so we can import from helpers
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from helpers.api_client import APIClient
from helpers.fixtures import data_factory
from helpers.db_utils import db_helper
from test_config import config


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Session-wide setup
    Runs once before all tests
    """
    print("\n" + "="*60)
    print("Setting up test environment...")
    print("="*60)

    # Check if backend is running
    try:
        client = APIClient()
        response = client.health_check()
        if response.status_code == 200:
            print("✓ Backend server is running")
        else:
            print("✗ Backend server returned unexpected status")
            pytest.exit("Backend server is not responding correctly", returncode=1)
    except Exception as e:
        print(f"✗ Cannot connect to backend server: {str(e)}")
        pytest.exit("Backend server is not running. Please start it on http://localhost:4000", returncode=1)

    # Connect to database
    if config.ENABLE_DB_CLEANUP:
        if db_helper.connect():
            print("✓ Connected to test database")
        else:
            print("✗ Failed to connect to test database")

    print("="*60 + "\n")

    yield

    # Teardown
    print("\n" + "="*60)
    print("Cleaning up test environment...")
    print("="*60)
    db_helper.disconnect()
    print("✓ Test environment cleaned up")
    print("="*60 + "\n")


@pytest.fixture(scope="function", autouse=True)
def cleanup_database():
    """
    Clean database before each test
    Runs before every test function
    """
    if config.ENABLE_DB_CLEANUP:
        # Optionally clear database before each test
        # db_helper.clear_all_collections()
        pass

    yield

    # Optionally clean up after test
    # This is commented out to allow inspection of test data after failures
    # db_helper.clear_all_collections()


@pytest.fixture(scope="function")
def api_client():
    """
    Provides a fresh API client for each test

    Usage:
        def test_something(api_client):
            response = api_client.get_courses()
    """
    client = APIClient()
    yield client
    client.close()


@pytest.fixture(scope="function")
def authenticated_client_student(api_client):
    """
    Provides an authenticated API client with a student user

    Usage:
        def test_something(authenticated_client_student):
            response = authenticated_client_student.get_courses()
    """
    # Create and sign in student
    student_data = data_factory.generate_user(role="STUDENT")
    api_client.signup(student_data)
    api_client.signin({
        "username": student_data["username"],
        "password": student_data["password"]
    })

    yield api_client

    # Clean up
    try:
        api_client.signout()
    except:
        pass


@pytest.fixture(scope="function")
def authenticated_client_faculty(api_client):
    """
    Provides an authenticated API client with a faculty user

    Usage:
        def test_something(authenticated_client_faculty):
            response = authenticated_client_faculty.create_course(course_data)
    """
    # Create and sign in faculty
    faculty_data = data_factory.generate_user(role="FACULTY")
    api_client.signup(faculty_data)
    api_client.signin({
        "username": faculty_data["username"],
        "password": faculty_data["password"]
    })

    yield api_client

    # Clean up
    try:
        api_client.signout()
    except:
        pass


@pytest.fixture(scope="function")
def authenticated_client_admin(api_client):
    """
    Provides an authenticated API client with an admin user
    """
    # Create and sign in admin
    admin_data = data_factory.generate_user(role="ADMIN")
    api_client.signup(admin_data)
    api_client.signin({
        "username": admin_data["username"],
        "password": admin_data["password"]
    })

    yield api_client

    # Clean up
    try:
        api_client.signout()
    except:
        pass


@pytest.fixture(scope="function")
def sample_user_data():
    """Provides sample user data"""
    return data_factory.generate_user()


@pytest.fixture(scope="function")
def sample_course_data():
    """Provides sample course data"""
    return data_factory.generate_course()


@pytest.fixture(scope="function")
def sample_course(authenticated_client_faculty):
    """
    Creates a sample course and returns its data

    Usage:
        def test_something(sample_course):
            course_id = sample_course["_id"]
    """
    course_data = data_factory.generate_course()
    response = authenticated_client_faculty.create_course(course_data)
    assert response.status_code == 200
    course = response.json()
    return course


@pytest.fixture(scope="function")
def sample_module_data():
    """Provides sample module data"""
    return {
        "name": "Sample Module",
        "description": "This is a sample module for testing"
    }


@pytest.fixture(scope="function")
def sample_assignment_data():
    """Provides sample assignment data"""
    return data_factory.generate_assignment("dummy_course_id")


@pytest.fixture(scope="function")
def sample_quiz_data():
    """Provides sample quiz data with questions"""
    quiz = data_factory.generate_quiz("dummy_course_id")
    quiz["questions"] = [
        data_factory.generate_multiple_choice_question(
            question="What is 2 + 2?",
            choices=["3", "4", "5", "6"],
            correctChoice=1
        ),
        data_factory.generate_true_false_question(
            question="Python is a programming language",
            correctAnswer=True
        ),
        data_factory.generate_fill_blank_question(
            question="The capital of France is [blank]",
            blanks=[{
                "possibleAnswers": ["Paris", "paris"],
                "caseSensitive": False,
                "points": 1
            }]
        )
    ]
    return quiz


# Custom markers
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "integration: Integration tests for API endpoints"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end workflow tests"
    )
    config.addinivalue_line(
        "markers", "auth: Authentication and authorization tests"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take longer to run"
    )
    config.addinivalue_line(
        "markers", "quiz: Quiz-related tests"
    )
