"""
API Client Helper
Provides a wrapper around the requests library for making HTTP calls to the backend API
with automatic session management and response handling
"""

import requests
from typing import Dict, Any, Optional
import json
from test_config import config


class APIClient:
    """HTTP client for API testing with session management"""

    def __init__(self, base_url: str = None):
        """
        Initialize API client

        Args:
            base_url: Base URL for the API (defaults to config.API_URL)
        """
        self.base_url = base_url or config.API_URL
        self.session = requests.Session()
        self.timeout = config.REQUEST_TIMEOUT
        self.current_user = None

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        files: Optional[Dict] = None
    ) -> requests.Response:
        """
        Make HTTP request

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (will be appended to base_url)
            data: Request body data (will be JSON serialized)
            params: URL query parameters
            headers: Additional headers
            files: Files to upload

        Returns:
            Response object
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Prepare headers
        request_headers = {"Content-Type": "application/json"}
        if headers:
            request_headers.update(headers)

        # Make request
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data if data and not files else None,
                params=params,
                headers=request_headers if not files else None,
                files=files,
                timeout=self.timeout
            )
            return response
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")

    def get(self, endpoint: str, params: Optional[Dict] = None) -> requests.Response:
        """Make GET request"""
        return self._make_request("GET", endpoint, params=params)

    def post(self, endpoint: str, data: Optional[Dict] = None, files: Optional[Dict] = None) -> requests.Response:
        """Make POST request"""
        return self._make_request("POST", endpoint, data=data, files=files)

    def put(self, endpoint: str, data: Optional[Dict] = None) -> requests.Response:
        """Make PUT request"""
        return self._make_request("PUT", endpoint, data=data)

    def delete(self, endpoint: str) -> requests.Response:
        """Make DELETE request"""
        return self._make_request("DELETE", endpoint)

    def signup(self, user_data: Dict) -> requests.Response:
        """
        Sign up a new user

        Args:
            user_data: User registration data (username, password, etc.)

        Returns:
            Response object
        """
        return self.post("users/signup", data=user_data)

    def signin(self, credentials: Dict) -> requests.Response:
        """
        Sign in a user and maintain session

        Args:
            credentials: Dict with 'username' and 'password'

        Returns:
            Response object
        """
        response = self.post("users/signin", data=credentials)
        if response.status_code == 200:
            self.current_user = response.json()
        return response

    def signout(self) -> requests.Response:
        """Sign out current user"""
        response = self.post("users/signout")
        if response.status_code == 200:
            self.current_user = None
        return response

    def get_profile(self) -> requests.Response:
        """Get current user profile"""
        return self.post("users/profile")

    def create_user(self, user_data: Dict) -> requests.Response:
        """Create a new user"""
        return self.post("users", data=user_data)

    def get_users(self, params: Optional[Dict] = None) -> requests.Response:
        """Get all users with optional filters"""
        return self.get("users", params=params)

    def get_user(self, user_id: str) -> requests.Response:
        """Get user by ID"""
        return self.get(f"users/{user_id}")

    def update_user(self, user_id: str, user_data: Dict) -> requests.Response:
        """Update user"""
        return self.put(f"users/{user_id}", data=user_data)

    def delete_user(self, user_id: str) -> requests.Response:
        """Delete user"""
        return self.delete(f"users/{user_id}")

    def create_course(self, course_data: Dict) -> requests.Response:
        """Create a new course (faculty only)"""
        return self.post("users/current/courses", data=course_data)

    def get_courses(self) -> requests.Response:
        """Get all courses"""
        return self.get("courses")

    def get_user_courses(self, user_id: str = "current") -> requests.Response:
        """Get courses for a user"""
        return self.get(f"users/{user_id}/courses")

    def update_course(self, course_id: str, course_data: Dict) -> requests.Response:
        """Update course (faculty only)"""
        return self.put(f"courses/{course_id}", data=course_data)

    def delete_course(self, course_id: str) -> requests.Response:
        """Delete course (faculty only)"""
        return self.delete(f"courses/{course_id}")

    def get_course_users(self, course_id: str) -> requests.Response:
        """Get users enrolled in a course"""
        return self.get(f"courses/{course_id}/users")

    def enroll_in_course(self, course_id: str, user_id: str = "current") -> requests.Response:
        """Enroll user in course"""
        if user_id == "current":
            return self.post(f"users/current/courses/{course_id}/enrollments")
        else:
            return self.post(f"users/{user_id}/courses/{course_id}")

    def unenroll_from_course(self, course_id: str, user_id: str = "current") -> requests.Response:
        """Unenroll user from course"""
        if user_id == "current":
            return self.delete(f"users/current/courses/{course_id}/enrollments")
        else:
            return self.delete(f"users/{user_id}/courses/{course_id}")

    def get_enrollments(self) -> requests.Response:
        """Get current user's enrollments"""
        return self.get("users/current/enrollments")

    def create_module(self, course_id: str, module_data: Dict) -> requests.Response:
        """Create module for course"""
        return self.post(f"courses/{course_id}/modules", data=module_data)

    def get_modules(self, course_id: str) -> requests.Response:
        """Get modules for course"""
        return self.get(f"courses/{course_id}/modules")

    def update_module(self, course_id: str, module_id: str, module_data: Dict) -> requests.Response:
        """Update module"""
        return self.put(f"courses/{course_id}/modules/{module_id}", data=module_data)

    def delete_module(self, course_id: str, module_id: str) -> requests.Response:
        """Delete module"""
        return self.delete(f"courses/{course_id}/modules/{module_id}")

    def create_assignment(self, course_id: str, assignment_data: Dict) -> requests.Response:
        """Create assignment for course"""
        return self.post(f"courses/{course_id}/assignments", data=assignment_data)

    def get_assignments(self, course_id: str) -> requests.Response:
        """Get assignments for course"""
        return self.get(f"courses/{course_id}/assignments")

    def update_assignment(self, assignment_id: str, assignment_data: Dict) -> requests.Response:
        """Update assignment"""
        return self.put(f"assignments/{assignment_id}", data=assignment_data)

    def delete_assignment(self, assignment_id: str) -> requests.Response:
        """Delete assignment"""
        return self.delete(f"assignments/{assignment_id}")

    def create_quiz(self, course_id: str, quiz_data: Dict) -> requests.Response:
        """Create quiz for course"""
        return self.post(f"courses/{course_id}/quizzes", data=quiz_data)

    def get_quizzes(self, course_id: str) -> requests.Response:
        """Get quizzes for course"""
        return self.get(f"courses/{course_id}/quizzes")

    def update_quiz(self, quiz_id: str, quiz_data: Dict) -> requests.Response:
        """Update quiz"""
        return self.put(f"quizzes/{quiz_id}", data=quiz_data)

    def delete_quiz(self, quiz_id: str) -> requests.Response:
        """Delete quiz"""
        return self.delete(f"quizzes/{quiz_id}")

    def debug_quiz(self, quiz_id: str) -> requests.Response:
        """Debug quiz data (faculty only)"""
        return self.get(f"quizzes/{quiz_id}/debug")

    def start_quiz_attempt(self, quiz_id: str) -> requests.Response:
        """Start a new quiz attempt"""
        return self.post(f"quizzes/{quiz_id}/attempts/start")

    def get_in_progress_attempt(self, quiz_id: str) -> requests.Response:
        """Get in-progress attempt"""
        return self.get(f"quizzes/{quiz_id}/attempts/in-progress")

    def update_attempt(self, attempt_id: str, answers: list) -> requests.Response:
        """Update attempt answers"""
        return self.put(f"attempts/{attempt_id}/update", data={"answers": answers})

    def submit_attempt(self, attempt_id: str, answers: list) -> requests.Response:
        """Submit quiz attempt"""
        return self.post(f"attempts/{attempt_id}/submit", data={"answers": answers})

    def get_quiz_attempts(self, quiz_id: str) -> requests.Response:
        """Get all attempts for a quiz"""
        return self.get(f"quizzes/{quiz_id}/attempts")

    def get_attempt_count(self, quiz_id: str) -> requests.Response:
        """Get completed attempt count"""
        return self.get(f"quizzes/{quiz_id}/attempts/count")

    def get_latest_attempt(self, quiz_id: str) -> requests.Response:
        """Get latest completed attempt"""
        return self.get(f"quizzes/{quiz_id}/attempts/latest")

    def get_attempt(self, attempt_id: str) -> requests.Response:
        """Get specific attempt details"""
        return self.get(f"attempts/{attempt_id}")

    def seed_database(self) -> requests.Response:
        """Seed database with initial data"""
        return self.post("seed")

    def reseed_database(self) -> requests.Response:
        """Clear and reseed database"""
        return self.post("reseed")

    def health_check(self) -> requests.Response:
        """Check API health"""
        return self.get("test")

    def close(self):
        """Close the session"""
        self.session.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
