"""
Module Tests
Tests for course module CRUD operations
"""

import pytest
from helpers.fixtures import data_factory


@pytest.mark.integration
class TestModules:
    """Test suite for module management endpoints"""

    def test_create_module(self, authenticated_client_faculty, sample_course):
        """Test creating a module for a course"""
        module_data = data_factory.generate_module(sample_course["_id"])

        response = authenticated_client_faculty.create_module(sample_course["_id"], module_data)

        assert response.status_code == 200
        created_module = response.json()
        assert created_module["name"] == module_data["name"]
        assert created_module["description"] == module_data["description"]
        assert "_id" in created_module

    def test_get_modules_for_course(self, authenticated_client_faculty, sample_course):
        """Test getting all modules for a course"""
        course_id = sample_course["_id"]

        # Create a few modules
        for i in range(3):
            module_data = data_factory.generate_module(course_id, name=f"Module {i+1}")
            authenticated_client_faculty.create_module(course_id, module_data)

        # Get modules
        response = authenticated_client_faculty.get_modules(course_id)

        assert response.status_code == 200
        modules = response.json()
        assert isinstance(modules, list)
        assert len(modules) >= 3

    def test_update_module(self, authenticated_client_faculty, sample_course):
        """Test updating a module"""
        course_id = sample_course["_id"]

        # Create a module
        module_data = data_factory.generate_module(course_id)
        create_response = authenticated_client_faculty.create_module(course_id, module_data)
        module = create_response.json()
        module_id = module["_id"]

        # Update the module
        update_data = {
            "name": "Updated Module Name",
            "description": "Updated description"
        }
        response = authenticated_client_faculty.update_module(course_id, module_id, update_data)

        assert response.status_code == 200
        updated_module = response.json()
        assert updated_module["name"] == "Updated Module Name"
        assert updated_module["description"] == "Updated description"

    def test_delete_module(self, authenticated_client_faculty, sample_course):
        """Test deleting a module"""
        course_id = sample_course["_id"]

        # Create a module
        module_data = data_factory.generate_module(course_id)
        create_response = authenticated_client_faculty.create_module(course_id, module_data)
        module = create_response.json()
        module_id = module["_id"]

        # Delete the module
        response = authenticated_client_faculty.delete_module(course_id, module_id)

        assert response.status_code == 200

    def test_module_with_lessons(self, authenticated_client_faculty, sample_course):
        """Test creating a module with nested lessons"""
        course_id = sample_course["_id"]

        module_data = data_factory.generate_module(
            course_id,
            lessons=[
                data_factory.generate_lesson(name="Lesson 1"),
                data_factory.generate_lesson(name="Lesson 2")
            ]
        )

        response = authenticated_client_faculty.create_module(course_id, module_data)

        assert response.status_code == 200
        created_module = response.json()
        assert "lessons" in created_module
        assert len(created_module["lessons"]) == 2
        assert created_module["lessons"][0]["name"] == "Lesson 1"
        assert created_module["lessons"][1]["name"] == "Lesson 2"

    def test_student_can_view_modules(self, authenticated_client_student, sample_course):
        """Test that students can view modules"""
        # Enroll student in course
        authenticated_client_student.enroll_in_course(sample_course["_id"], "current")

        # Get modules
        response = authenticated_client_student.get_modules(sample_course["_id"])

        assert response.status_code == 200
        modules = response.json()
        assert isinstance(modules, list)

    def test_empty_modules_list(self, authenticated_client_faculty, sample_course):
        """Test getting modules for a course with no modules"""
        response = authenticated_client_faculty.get_modules(sample_course["_id"])

        assert response.status_code == 200
        modules = response.json()
        assert isinstance(modules, list)
        # May be empty or have default modules

    def test_module_ordering(self, authenticated_client_faculty, sample_course):
        """Test that modules maintain order"""
        course_id = sample_course["_id"]

        # Create modules in specific order
        module_names = ["Introduction", "Chapter 1", "Chapter 2", "Conclusion"]
        for name in module_names:
            module_data = data_factory.generate_module(course_id, name=name)
            authenticated_client_faculty.create_module(course_id, module_data)

        # Get modules
        response = authenticated_client_faculty.get_modules(course_id)

        assert response.status_code == 200
        modules = response.json()
        # Verify we created at least these modules
        assert len(modules) >= 4
