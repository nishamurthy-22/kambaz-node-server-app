"""
Assignment Tests
Tests for assignment CRUD operations
"""

import pytest
from helpers.fixtures import data_factory
from datetime import datetime, timedelta


@pytest.mark.integration
class TestAssignments:
    """Test suite for assignment management endpoints"""

    def test_create_assignment(self, authenticated_client_faculty, sample_course):
        """Test creating an assignment for a course"""
        course_id = sample_course["_id"]
        assignment_data = data_factory.generate_assignment(course_id)

        response = authenticated_client_faculty.create_assignment(course_id, assignment_data)

        assert response.status_code == 200
        created_assignment = response.json()
        assert created_assignment["title"] == assignment_data["title"]
        assert created_assignment["course"] == course_id
        assert created_assignment["points"] == assignment_data["points"]
        assert "_id" in created_assignment

    def test_get_assignments_for_course(self, authenticated_client_faculty, sample_course):
        """Test getting all assignments for a course"""
        course_id = sample_course["_id"]

        # Create multiple assignments
        for i in range(3):
            assignment_data = data_factory.generate_assignment(
                course_id,
                title=f"Assignment {i+1}"
            )
            authenticated_client_faculty.create_assignment(course_id, assignment_data)

        # Get assignments
        response = authenticated_client_faculty.get_assignments(course_id)

        assert response.status_code == 200
        assignments = response.json()
        assert isinstance(assignments, list)
        assert len(assignments) >= 3

    def test_update_assignment(self, authenticated_client_faculty, sample_course):
        """Test updating an assignment"""
        course_id = sample_course["_id"]

        # Create an assignment
        assignment_data = data_factory.generate_assignment(course_id)
        create_response = authenticated_client_faculty.create_assignment(course_id, assignment_data)
        assignment = create_response.json()
        assignment_id = assignment["_id"]

        # Update the assignment
        update_data = {
            "title": "Updated Assignment Title",
            "points": 150,
            "description": "Updated description"
        }
        response = authenticated_client_faculty.update_assignment(assignment_id, update_data)

        assert response.status_code == 200
        updated_assignment = response.json()
        assert updated_assignment["title"] == "Updated Assignment Title"
        assert updated_assignment["points"] == 150
        assert updated_assignment["description"] == "Updated description"

    def test_delete_assignment(self, authenticated_client_faculty, sample_course):
        """Test deleting an assignment"""
        course_id = sample_course["_id"]

        # Create an assignment
        assignment_data = data_factory.generate_assignment(course_id)
        create_response = authenticated_client_faculty.create_assignment(course_id, assignment_data)
        assignment = create_response.json()
        assignment_id = assignment["_id"]

        # Delete the assignment
        response = authenticated_client_faculty.delete_assignment(assignment_id)

        assert response.status_code == 200

    def test_assignment_with_dates(self, authenticated_client_faculty, sample_course):
        """Test creating assignment with date fields"""
        course_id = sample_course["_id"]

        assignment_data = data_factory.generate_assignment(
            course_id,
            **{
                "Not available until": "2024-01-01",
                "Due": "2024-01-15",
                "Available until": "2024-01-30"
            }
        )

        response = authenticated_client_faculty.create_assignment(course_id, assignment_data)

        assert response.status_code == 200
        assignment = response.json()
        assert assignment["Not available until"] == "2024-01-01"
        assert assignment["Due"] == "2024-01-15"
        assert assignment["Available until"] == "2024-01-30"

    def test_assignment_points_validation(self, authenticated_client_faculty, sample_course):
        """Test that assignment points are properly stored"""
        course_id = sample_course["_id"]

        assignment_data = data_factory.generate_assignment(course_id, points=100)

        response = authenticated_client_faculty.create_assignment(course_id, assignment_data)

        assert response.status_code == 200
        assignment = response.json()
        assert assignment["points"] == 100

    def test_student_can_view_assignments(self, authenticated_client_student, sample_course):
        """Test that students can view assignments"""
        # Enroll student in course
        authenticated_client_student.enroll_in_course(sample_course["_id"], "current")

        # Get assignments
        response = authenticated_client_student.get_assignments(sample_course["_id"])

        assert response.status_code == 200
        assignments = response.json()
        assert isinstance(assignments, list)

    def test_student_cannot_create_assignment(self, authenticated_client_student, sample_course):
        """Test that students cannot create assignments"""
        course_id = sample_course["_id"]
        assignment_data = data_factory.generate_assignment(course_id)

        response = authenticated_client_student.create_assignment(course_id, assignment_data)

        # Should fail with authorization error
        assert response.status_code in [401, 403, 500]

    def test_student_cannot_delete_assignment(self, authenticated_client_student, authenticated_client_faculty, sample_course):
        """Test that students cannot delete assignments"""
        course_id = sample_course["_id"]

        # Faculty creates assignment
        assignment_data = data_factory.generate_assignment(course_id)
        create_response = authenticated_client_faculty.create_assignment(course_id, assignment_data)
        assignment = create_response.json()

        # Student tries to delete
        response = authenticated_client_student.delete_assignment(assignment["_id"])

        # Should fail with authorization error
        assert response.status_code in [401, 403, 500]

    def test_empty_assignments_list(self, authenticated_client_faculty, sample_course):
        """Test getting assignments for a course with no assignments"""
        response = authenticated_client_faculty.get_assignments(sample_course["_id"])

        assert response.status_code == 200
        assignments = response.json()
        assert isinstance(assignments, list)
        # May be empty
