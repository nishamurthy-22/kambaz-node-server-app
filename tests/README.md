# Kambaz Backend API Test Suite

Comprehensive automated testing suite for the Kambaz Learning Management System backend API.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running Tests](#running-tests)
- [Test Structure](#test-structure)
- [Test Coverage](#test-coverage)
- [Configuration](#configuration)
- [Reports](#reports)
- [Writing New Tests](#writing-new-tests)
- [Troubleshooting](#troubleshooting)

## Overview

This test suite provides comprehensive coverage for the Kambaz backend API, including:
- User authentication and authorization
- Course management
- Enrollment operations
- Modules and assignments
- Quiz creation and grading
- End-to-end user workflows

## Features

- **Modular Test Organization**: Tests are organized by feature domain
- **Comprehensive Coverage**: Integration and E2E tests for all API endpoints
- **Automatic Session Management**: Built-in authentication handling
- **Test Data Generation**: Realistic test data using Faker
- **Multiple Report Formats**: HTML and JSON test reports
- **Parallel Execution**: Run tests in parallel for faster execution
- **Flexible Test Selection**: Run all tests or filter by category/module

## Prerequisites

Before running the tests, ensure you have:

1. **Python 3.8+** installed
2. **Backend server** running on `http://localhost:4000`
3. **MongoDB** accessible (for database verification)

## Installation

### 1. Navigate to the tests directory

```bash
cd kambaz-node-server-app/tests
```

### 2. Create a virtual environment (recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Running Tests

### Start the Backend Server

**IMPORTANT**: Before running tests, make sure the backend server is running:

```bash
# In the kambaz-node-server-app directory
npm start
```

The server should be running on `http://localhost:4000`

### Run All Tests

```bash
python main.py
```

### Run Specific Test Categories

```bash
# Run only integration tests
python main.py --integration

# Run only E2E tests
python main.py --e2e

# Run only authentication tests
python main.py --auth

# Run only quiz-related tests
python main.py --quiz
```

### Run Specific Test Modules

```bash
# List available modules
python main.py --list-modules

# Run specific module
python main.py --module auth
python main.py --module users
python main.py --module courses
python main.py --module quizzes
python main.py --module quiz_attempts
python main.py --module student_workflow
python main.py --module faculty_workflow
```

### Run Tests with Reports

```bash
# Generate HTML report
python main.py --html

# Generate JSON report
python main.py --json

# Generate both reports
python main.py --html --json
```

### Run Tests in Parallel

```bash
# Run with parallel execution
python main.py --parallel

# Run integration tests in parallel with HTML report
python main.py --integration --parallel --html
```

### Advanced Options

```bash
# Verbose output
python main.py --verbose

# Quiet output
python main.py --quiet

# Run specific test file
python main.py --path integration/test_auth.py

# Run specific test function
python main.py --path integration/test_auth.py::TestAuthentication::test_user_signup_success
```

## Test Structure

```
tests/
├── __init__.py
├── main.py                          # Main test runner
├── conftest.py                      # Pytest configuration and fixtures
├── test_config.py                   # Test configuration
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
│
├── integration/                     # Integration tests
│   ├── __init__.py
│   ├── test_auth.py                # Authentication tests
│   ├── test_users.py               # User management tests
│   ├── test_courses.py             # Course management tests
│   ├── test_enrollments.py         # Enrollment tests
│   ├── test_modules.py             # Module tests
│   ├── test_assignments.py         # Assignment tests
│   ├── test_quizzes.py             # Quiz management tests
│   └── test_quiz_attempts.py       # Quiz submission/grading tests
│
├── e2e/                             # End-to-end tests
│   ├── __init__.py
│   ├── test_student_workflow.py    # Complete student journey
│   └── test_faculty_workflow.py    # Complete faculty journey
│
└── helpers/                         # Test utilities
    ├── __init__.py
    ├── api_client.py               # HTTP client wrapper
    ├── fixtures.py                 # Test data factories
    └── db_utils.py                 # Database utilities
```

## Test Coverage

### Authentication (test_auth.py)
- ✅ User signup (valid/invalid data)
- ✅ User signin (correct/incorrect credentials)
- ✅ Session persistence
- ✅ Session invalidation on signout
- ✅ Profile retrieval
- ✅ Multiple user roles

### User Management (test_users.py)
- ✅ Create, read, update, delete users
- ✅ Filter users by role
- ✅ Filter users by name
- ✅ Unique username constraint
- ✅ All user roles (STUDENT, FACULTY, ADMIN, TA, USER)

### Course Management (test_courses.py)
- ✅ CRUD operations for courses
- ✅ Faculty authorization checks
- ✅ Auto-enrollment of course creator
- ✅ Cascade deletion (enrollments, assignments)
- ✅ Course user listing

### Enrollments (test_enrollments.py)
- ✅ Student enrollment/unenrollment
- ✅ Faculty enrolling students
- ✅ Duplicate enrollment prevention
- ✅ Enrollment status management

### Modules (test_modules.py)
- ✅ CRUD operations for modules
- ✅ Nested lessons within modules
- ✅ Module ordering

### Assignments (test_assignments.py)
- ✅ CRUD operations for assignments
- ✅ Date validation
- ✅ Points validation
- ✅ Student/faculty authorization

### Quizzes (test_quizzes.py)
- ✅ Create quizzes with multiple question types
- ✅ Multiple choice questions
- ✅ True/false questions
- ✅ Fill in the blank questions
- ✅ Answer stripping for students
- ✅ Quiz settings (time limits, attempts, etc.)
- ✅ Debug endpoint for faculty

### Quiz Attempts (test_quiz_attempts.py)
- ✅ Start quiz attempt
- ✅ Update answers while in progress
- ✅ Submit quiz for grading
- ✅ Server-side answer validation
- ✅ Multiple attempts support
- ✅ Case sensitivity handling
- ✅ Partial credit for multi-blank questions

### E2E Workflows
- ✅ Complete student journey (signup → enroll → quiz → results)
- ✅ Complete faculty journey (create course → add content → manage)
- ✅ Multiple quiz attempts
- ✅ Student/faculty permission differences

## Configuration

Configuration is managed in `test_config.py`. Key settings:

```python
# Backend URL
BASE_URL = "http://localhost:4000"

# Database
DB_CONNECTION_STRING = "mongodb://127.0.0.1:27017/kambaz_test"

# Test Settings
ENABLE_DB_CLEANUP = True
ENABLE_PARALLEL_TESTS = False
ENABLE_HTML_REPORT = True
ENABLE_JSON_REPORT = True
PARALLEL_WORKERS = 4
```

### Environment Variables

You can override settings using environment variables:

```bash
# Windows
set TEST_BASE_URL=http://localhost:5000
python main.py

# Linux/Mac
export TEST_BASE_URL=http://localhost:5000
python main.py
```

## Reports

### HTML Report

After running tests with `--html`, open the generated report:

```bash
# The report is saved as test_report.html
# Open it in your browser
```

The HTML report includes:
- Test execution summary
- Pass/fail status for each test
- Execution time
- Detailed error messages and stack traces
- Environment information

### JSON Report

The JSON report (`test_report.json`) contains:
- Structured test results
- Detailed test metadata
- Can be parsed by CI/CD tools

## Writing New Tests

### 1. Create a new test file

```python
# tests/integration/test_new_feature.py

import pytest
from helpers.fixtures import data_factory


@pytest.mark.integration
class TestNewFeature:
    """Test suite for new feature"""

    def test_something(self, authenticated_client_student):
        """Test description"""
        # Arrange
        test_data = data_factory.generate_user()

        # Act
        response = authenticated_client_student.some_endpoint(test_data)

        # Assert
        assert response.status_code == 200
        assert response.json()["field"] == "expected_value"
```

### 2. Use available fixtures

Available fixtures (defined in `conftest.py`):
- `api_client`: Unauthenticated API client
- `authenticated_client_student`: Student user client
- `authenticated_client_faculty`: Faculty user client
- `authenticated_client_admin`: Admin user client
- `sample_course`: Pre-created course
- `sample_user_data`: Sample user data
- `sample_course_data`: Sample course data

### 3. Add custom markers

```python
@pytest.mark.slow
@pytest.mark.integration
def test_long_running_operation(api_client):
    # Test code
    pass
```

## Troubleshooting

### Backend Server Not Running

**Error**: `Cannot connect to backend server`

**Solution**: Start the backend server:
```bash
cd kambaz-node-server-app
npm start
```

### Database Connection Issues

**Error**: `Failed to connect to test database`

**Solution**: Ensure MongoDB is running and accessible

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'pytest'`

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### Test Failures Due to Data

**Issue**: Tests fail because of existing data

**Solution**: Clear the test database or use the reseed endpoint:
```python
api_client.reseed_database()
```

### Permission Denied Errors

**Issue**: Tests fail with 401/403 errors

**Solution**: Check that:
1. User is properly authenticated
2. User has correct role (STUDENT, FACULTY, etc.)
3. Session is being maintained

## Best Practices

1. **Keep tests independent**: Each test should be able to run in isolation
2. **Use fixtures**: Leverage pytest fixtures for common setup
3. **Clear test names**: Use descriptive test function names
4. **Test one thing**: Each test should verify one specific behavior
5. **Clean up**: Tests should clean up after themselves (fixtures handle this)
6. **Use data factories**: Generate test data with the `data_factory`

## CI/CD Integration

To integrate with CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    cd tests
    pip install -r requirements.txt
    python main.py --html --json
```

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review test output and error messages
3. Check backend server logs
4. Verify MongoDB is running and accessible

## License

This test suite is part of the Kambaz project.
