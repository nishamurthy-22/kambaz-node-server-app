"""
Enrollment Tests
Tests for course enrollment and unenrollment operations
"""

import pytest
from helpers.fixtures import data_factory


@pytest.mark.integration
class TestEnrollments:
    """Test suite for enrollment endpoints"""

    def test_student_enroll_in_course(self, authenticated_client_student, sample_course):
        """Test student can enroll in a course"""
        course_id = sample_course["_id"]

        response = authenticated_client_student.enroll_in_course(course_id, "current")

        assert response.status_code == 200
        enrollment = response.json()
        assert enrollment["course"] == course_id
        assert enrollment["status"] == "ENROLLED"

    def test_student_get_enrollments(self, authenticated_client_student, sample_course):
        """Test student can get their enrollments"""
        # Enroll in course
        authenticated_client_student.enroll_in_course(sample_course["_id"], "current")

        # Get enrollments
        response = authenticated_client_student.get_enrollments()

        assert response.status_code == 200
        enrollments = response.json()
        assert isinstance(enrollments, list)
        assert len(enrollments) >= 1

        # Check that the enrollment exists
        course_ids = [e["course"] for e in enrollments]
        assert sample_course["_id"] in course_ids

    def test_student_unenroll_from_course(self, authenticated_client_student, sample_course):
        """Test student can unenroll from a course"""
        course_id = sample_course["_id"]

        # Enroll first
        enroll_response = authenticated_client_student.enroll_in_course(course_id, "current")
        assert enroll_response.status_code == 200

        # Unenroll
        response = authenticated_client_student.unenroll_from_course(course_id, "current")

        assert response.status_code == 200

    def test_get_course_users(self, authenticated_client_faculty, authenticated_client_student, sample_course):
        """Test getting all users enrolled in a course"""
        # Student enrolls in course
        student_client = authenticated_client_student
        student_client.enroll_in_course(sample_course["_id"], "current")

        # Faculty gets course users
        response = authenticated_client_faculty.get_course_users(sample_course["_id"])

        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        # Should have at least faculty and student
        assert len(users) >= 2

    def test_prevent_duplicate_enrollments(self, authenticated_client_student, sample_course):
        """Test that enrolling twice in same course is handled"""
        course_id = sample_course["_id"]

        # First enrollment
        response1 = authenticated_client_student.enroll_in_course(course_id, "current")
        assert response1.status_code == 200

        # Second enrollment (should fail or return same enrollment)
        response2 = authenticated_client_student.enroll_in_course(course_id, "current")
        # Depending on backend implementation, might return 200, 400, or 409
        assert response2.status_code in [200, 400, 409]

    def test_enrollment_has_default_status(self, authenticated_client_student, sample_course):
        """Test that new enrollments have ENROLLED status"""
        response = authenticated_client_student.enroll_in_course(sample_course["_id"], "current")

        assert response.status_code == 200
        enrollment = response.json()
        assert enrollment["status"] == "ENROLLED"

    def test_faculty_can_enroll_student(self, api_client, sample_course):
        """Test faculty can enroll a student in their course"""
        # Create a student
        student_data = data_factory.generate_user(role="STUDENT")
        signup_response = api_client.signup(student_data)
        student = signup_response.json()
        student_id = student["_id"]

        # Faculty enrolls the student (need faculty auth)
        faculty_data = data_factory.generate_user(role="FACULTY")
        api_client.signup(faculty_data)
        api_client.signin({
            "username": faculty_data["username"],
            "password": faculty_data["password"]
        })

        # Create course as faculty
        course_data = data_factory.generate_course()
        course_response = api_client.create_course(course_data)
        course = course_response.json()

        # Enroll student in course
        response = api_client.enroll_in_course(course["_id"], student_id)

        assert response.status_code == 200

    def test_unenrollment_removes_from_course_users(self, authenticated_client_student, sample_course):
        """Test that unenrolling removes user from course users list"""
        course_id = sample_course["_id"]

        # Enroll
        authenticated_client_student.enroll_in_course(course_id, "current")

        # Unenroll
        authenticated_client_student.unenroll_from_course(course_id, "current")

        # Check enrollments
        enrollments_response = authenticated_client_student.get_enrollments()
        assert enrollments_response.status_code == 200
        enrollments = enrollments_response.json()

        # Filter out enrollments for this course that are still active
        active_enrollments = [e for e in enrollments if e.get("course") == course_id and e.get("status") == "ENROLLED"]
        assert len(active_enrollments) == 0

    def test_multiple_students_enroll_in_same_course(self, api_client, sample_course):
        """Test multiple students can enroll in the same course"""
        course_id = sample_course["_id"]
        enrolled_students = []

        # Create and enroll 3 students
        for i in range(3):
            student_data = data_factory.generate_user(role="STUDENT")
            api_client.signup(student_data)
            api_client.signin({
                "username": student_data["username"],
                "password": student_data["password"]
            })

            enroll_response = api_client.enroll_in_course(course_id, "current")
            assert enroll_response.status_code == 200

            enrolled_students.append(student_data["username"])
            api_client.signout()

        # All students should be enrolled
        assert len(enrolled_students) == 3
