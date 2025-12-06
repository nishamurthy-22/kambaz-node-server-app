"""
User Management Tests
Tests for user CRUD operations and filtering
"""

import pytest
from helpers.fixtures import data_factory


@pytest.mark.integration
class TestUserManagement:
    """Test suite for user management endpoints"""

    def test_create_user(self, authenticated_client_admin):
        """Test creating a new user"""
        user_data = data_factory.generate_user(role="STUDENT")

        response = authenticated_client_admin.create_user(user_data)

        assert response.status_code == 200
        created_user = response.json()
        assert created_user["username"] == user_data["username"]
        assert created_user["role"] == "STUDENT"
        assert "_id" in created_user

    def test_get_all_users(self, authenticated_client_admin):
        """Test getting all users"""
        # Create a few users
        for i in range(3):
            user_data = data_factory.generate_user()
            authenticated_client_admin.create_user(user_data)

        response = authenticated_client_admin.get_users()

        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        assert len(users) >= 3

    def test_get_user_by_id(self, authenticated_client_admin):
        """Test getting a user by ID"""
        # Create a user
        user_data = data_factory.generate_user()
        create_response = authenticated_client_admin.create_user(user_data)
        user_id = create_response.json()["_id"]

        # Get the user by ID
        response = authenticated_client_admin.get_user(user_id)

        assert response.status_code == 200
        user = response.json()
        assert user["_id"] == user_id
        assert user["username"] == user_data["username"]

    def test_get_user_by_id_not_found(self, authenticated_client_admin):
        """Test getting non-existent user returns 404"""
        response = authenticated_client_admin.get_user("nonexistent_id_12345")

        assert response.status_code in [404, 500]

    def test_update_user(self, authenticated_client_admin):
        """Test updating a user"""
        # Create a user
        user_data = data_factory.generate_user()
        create_response = authenticated_client_admin.create_user(user_data)
        user_id = create_response.json()["_id"]

        # Update the user
        update_data = {
            "firstName": "UpdatedFirst",
            "lastName": "UpdatedLast",
            "email": "updated@test.com"
        }
        response = authenticated_client_admin.update_user(user_id, update_data)

        assert response.status_code == 200
        updated_user = response.json()
        assert updated_user["firstName"] == "UpdatedFirst"
        assert updated_user["lastName"] == "UpdatedLast"
        assert updated_user["email"] == "updated@test.com"

    def test_update_own_profile(self, authenticated_client_student):
        """Test user can update their own profile"""
        # Get current user ID
        profile_response = authenticated_client_student.get_profile()
        user_id = profile_response.json()["_id"]

        # Update own profile
        update_data = {
            "firstName": "NewFirstName",
            "lastName": "NewLastName"
        }
        response = authenticated_client_student.update_user(user_id, update_data)

        assert response.status_code == 200
        updated_user = response.json()
        assert updated_user["firstName"] == "NewFirstName"
        assert updated_user["lastName"] == "NewLastName"

    def test_delete_user(self, authenticated_client_admin):
        """Test deleting a user"""
        # Create a user
        user_data = data_factory.generate_user()
        create_response = authenticated_client_admin.create_user(user_data)
        user_id = create_response.json()["_id"]

        # Delete the user
        response = authenticated_client_admin.delete_user(user_id)

        assert response.status_code == 200

        # Verify user is deleted
        get_response = authenticated_client_admin.get_user(user_id)
        assert get_response.status_code in [404, 500]

    def test_filter_users_by_role(self, authenticated_client_admin):
        """Test filtering users by role"""
        # Create users with different roles
        faculty_data = data_factory.generate_user(role="FACULTY")
        student_data = data_factory.generate_user(role="STUDENT")

        authenticated_client_admin.create_user(faculty_data)
        authenticated_client_admin.create_user(student_data)

        # Filter by FACULTY role
        response = authenticated_client_admin.get_users(params={"role": "FACULTY"})

        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        # All returned users should be FACULTY
        for user in users:
            assert user["role"] == "FACULTY"

    def test_filter_users_by_name(self, authenticated_client_admin):
        """Test filtering users by name"""
        # Create a user with specific name
        user_data = data_factory.generate_user(
            firstName="UniqueFirstName",
            lastName="UniqueLastName"
        )
        authenticated_client_admin.create_user(user_data)

        # Search by first name
        response = authenticated_client_admin.get_users(params={"name": "UniqueFirstName"})

        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        # Should find at least one user with matching name
        assert len(users) > 0
        found = any("UniqueFirstName" in user.get("firstName", "") for user in users)
        assert found

    def test_create_users_with_all_roles(self, authenticated_client_admin):
        """Test creating users with all possible roles"""
        roles = ["STUDENT", "FACULTY", "ADMIN", "TA", "USER"]

        for role in roles:
            user_data = data_factory.generate_user(role=role)
            response = authenticated_client_admin.create_user(user_data)

            assert response.status_code == 200
            created_user = response.json()
            assert created_user["role"] == role

    def test_user_fields_validation(self, authenticated_client_admin):
        """Test that user fields are properly stored"""
        user_data = data_factory.generate_user(
            role="STUDENT",
            section="Section A",
            dob="1995-05-15"
        )

        response = authenticated_client_admin.create_user(user_data)

        assert response.status_code == 200
        created_user = response.json()
        assert created_user["section"] == "Section A"
        assert "dob" in created_user

    def test_unique_username_constraint(self, authenticated_client_admin):
        """Test that username must be unique"""
        user_data = data_factory.generate_user()

        # Create first user
        response1 = authenticated_client_admin.create_user(user_data)
        assert response1.status_code == 200

        # Try to create second user with same username
        response2 = authenticated_client_admin.create_user(user_data)
        assert response2.status_code in [400, 409, 500]  # Bad request, conflict, or server error

    def test_get_users_pagination(self, authenticated_client_admin):
        """Test getting users returns a list (basic pagination check)"""
        response = authenticated_client_admin.get_users()

        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        # Verify each user has required fields
        if len(users) > 0:
            for user in users[:3]:  # Check first 3 users
                assert "_id" in user
                assert "username" in user
                assert "role" in user
