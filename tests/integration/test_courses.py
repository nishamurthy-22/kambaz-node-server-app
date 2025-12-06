"""
Course Management Tests
Tests for course CRUD operations and authorization
"""

import pytest
from helpers.fixtures import data_factory


@pytest.mark.integration
class TestCourseManagement:
    """Test suite for course management endpoints"""

    def test_faculty_create_course(self, authenticated_client_faculty):
        """Test faculty can create a course"""
        course_data = data_factory.generate_course()

        response = authenticated_client_faculty.create_course(course_data)

        assert response.status_code == 200
        created_course = response.json()
        assert created_course["name"] == course_data["name"]
        assert created_course["number"] == course_data["number"]
        assert created_course["credits"] == course_data["credits"]
        assert "_id" in created_course

    def test_faculty_auto_enrolled_in_created_course(self, authenticated_client_faculty):
        """Test that faculty is auto-enrolled when creating a course"""
        course_data = data_factory.generate_course()

        # Create course
        create_response = authenticated_client_faculty.create_course(course_data)
        assert create_response.status_code == 200
        course = create_response.json()

        # Check faculty's courses
        courses_response = authenticated_client_faculty.get_user_courses("current")
        assert courses_response.status_code == 200
        courses = courses_response.json()

        # Faculty should be enrolled in the created course
        course_ids = [c["_id"] for c in courses]
        assert course["_id"] in course_ids

    def test_student_cannot_create_course(self, authenticated_client_student):
        """Test that students cannot create courses"""
        course_data = data_factory.generate_course()

        response = authenticated_client_student.create_course(course_data)

        # Should fail with authorization error
        assert response.status_code in [401, 403, 500]

    def test_get_all_courses(self, authenticated_client_student, sample_course):
        """Test getting all courses"""
        response = authenticated_client_student.get_courses()

        assert response.status_code == 200
        courses = response.json()
        assert isinstance(courses, list)
        assert len(courses) >= 1

        # Verify sample_course is in the list
        course_ids = [c["_id"] for c in courses]
        assert sample_course["_id"] in course_ids

    def test_get_user_courses(self, authenticated_client_faculty):
        """Test getting courses for a specific user"""
        # Create a course (faculty will be auto-enrolled)
        course_data = data_factory.generate_course()
        create_response = authenticated_client_faculty.create_course(course_data)
        course = create_response.json()

        # Get user's courses
        response = authenticated_client_faculty.get_user_courses("current")

        assert response.status_code == 200
        courses = response.json()
        assert isinstance(courses, list)
        assert len(courses) >= 1

        # Created course should be in the list
        course_ids = [c["_id"] for c in courses]
        assert course["_id"] in course_ids

    def test_update_course_by_faculty(self, authenticated_client_faculty, sample_course):
        """Test faculty can update their course"""
        update_data = {
            "name": "Updated Course Name",
            "description": "Updated description",
            "credits": 4
        }

        response = authenticated_client_faculty.update_course(sample_course["_id"], update_data)

        assert response.status_code == 200
        updated_course = response.json()
        assert updated_course["name"] == "Updated Course Name"
        assert updated_course["description"] == "Updated description"
        assert updated_course["credits"] == 4

    def test_student_cannot_update_course(self, authenticated_client_student, sample_course):
        """Test students cannot update courses"""
        update_data = {
            "name": "Hacked Course Name"
        }

        response = authenticated_client_student.update_course(sample_course["_id"], update_data)

        # Should fail with authorization error
        assert response.status_code in [401, 403, 500]

    def test_delete_course_by_faculty(self, authenticated_client_faculty):
        """Test faculty can delete their course"""
        # Create a course
        course_data = data_factory.generate_course()
        create_response = authenticated_client_faculty.create_course(course_data)
        course = create_response.json()

        # Delete the course
        response = authenticated_client_faculty.delete_course(course["_id"])

        assert response.status_code == 200

    def test_delete_course_cascades(self, authenticated_client_faculty):
        """Test deleting a course also deletes enrollments and assignments"""
        # Create a course
        course_data = data_factory.generate_course()
        create_response = authenticated_client_faculty.create_course(course_data)
        course = create_response.json()
        course_id = course["_id"]

        # Create an assignment for the course
        assignment_data = data_factory.generate_assignment(course_id)
        authenticated_client_faculty.create_assignment(course_id, assignment_data)

        # Delete the course
        delete_response = authenticated_client_faculty.delete_course(course_id)
        assert delete_response.status_code == 200

        # Assignments should also be deleted (verify by trying to get them)
        assignments_response = authenticated_client_faculty.get_assignments(course_id)
        # The endpoint might return 404 or empty list depending on implementation
        assert assignments_response.status_code in [200, 404]
        if assignments_response.status_code == 200:
            assignments = assignments_response.json()
            assert len(assignments) == 0

    def test_student_cannot_delete_course(self, authenticated_client_student, sample_course):
        """Test students cannot delete courses"""
        response = authenticated_client_student.delete_course(sample_course["_id"])

        # Should fail with authorization error
        assert response.status_code in [401, 403, 500]

    def test_get_course_users(self, authenticated_client_faculty, sample_course):
        """Test getting all users enrolled in a course"""
        response = authenticated_client_faculty.get_course_users(sample_course["_id"])

        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        # At least the faculty member should be enrolled
        assert len(users) >= 1

    def test_course_has_required_fields(self, authenticated_client_faculty):
        """Test that created course has all required fields"""
        course_data = data_factory.generate_course(
            name="Test Course",
            number="CS101",
            credits=3,
            department="Computer Science",
            description="A test course"
        )

        response = authenticated_client_faculty.create_course(course_data)

        assert response.status_code == 200
        course = response.json()
        assert course["name"] == "Test Course"
        assert course["number"] == "CS101"
        assert course["credits"] == 3
        assert course["department"] == "Computer Science"
        assert course["description"] == "A test course"
        assert "_id" in course

    def test_course_with_dates(self, authenticated_client_faculty):
        """Test creating course with start and end dates"""
        course_data = data_factory.generate_course(
            startDate="2024-01-15",
            endDate="2024-05-15"
        )

        response = authenticated_client_faculty.create_course(course_data)

        assert response.status_code == 200
        course = response.json()
        assert course["startDate"] == "2024-01-15"
        assert course["endDate"] == "2024-05-15"

    def test_multiple_faculty_create_courses(self, api_client):
        """Test multiple faculty can create their own courses"""
        # Create first faculty
        faculty1_data = data_factory.generate_user(role="FACULTY")
        api_client.signup(faculty1_data)
        api_client.signin({
            "username": faculty1_data["username"],
            "password": faculty1_data["password"]
        })

        course1_data = data_factory.generate_course(name="Course by Faculty 1")
        response1 = api_client.create_course(course1_data)
        assert response1.status_code == 200
        course1 = response1.json()

        # Sign out and create second faculty
        api_client.signout()

        faculty2_data = data_factory.generate_user(role="FACULTY")
        api_client.signup(faculty2_data)
        api_client.signin({
            "username": faculty2_data["username"],
            "password": faculty2_data["password"]
        })

        course2_data = data_factory.generate_course(name="Course by Faculty 2")
        response2 = api_client.create_course(course2_data)
        assert response2.status_code == 200
        course2 = response2.json()

        # Both courses should exist and be different
        assert course1["_id"] != course2["_id"]
        assert course1["name"] != course2["name"]
