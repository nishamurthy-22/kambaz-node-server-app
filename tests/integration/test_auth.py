"""
Authentication Tests
Tests for user signup, signin, signout, and session management
"""

import pytest
from helpers.fixtures import data_factory


@pytest.mark.integration
@pytest.mark.auth
class TestAuthentication:
    """Test suite for authentication endpoints"""

    def test_user_signup_success(self, api_client):
        """Test successful user signup"""
        user_data = data_factory.generate_user(role="STUDENT")

        response = api_client.signup(user_data)

        assert response.status_code == 200
        created_user = response.json()
        assert created_user["username"] == user_data["username"]
        assert created_user["email"] == user_data["email"]
        assert created_user["role"] == "STUDENT"
        assert "_id" in created_user
        assert "password" not in created_user or created_user.get("password") == user_data["password"]  # Check backend behavior

    def test_user_signup_duplicate_username(self, api_client):
        """Test signup with duplicate username fails"""
        user_data = data_factory.generate_user(role="STUDENT")

        # First signup should succeed
        response1 = api_client.signup(user_data)
        assert response1.status_code == 200

        # Second signup with same username should fail
        response2 = api_client.signup(user_data)
        assert response2.status_code in [400, 409]  # Bad request or conflict

    def test_user_signup_missing_required_fields(self, api_client):
        """Test signup with missing required fields fails"""
        # Missing username
        user_data = data_factory.generate_user()
        del user_data["username"]
        response = api_client.signup(user_data)
        assert response.status_code in [400, 500]

        # Missing password
        user_data = data_factory.generate_user()
        del user_data["password"]
        response = api_client.signup(user_data)
        assert response.status_code in [400, 500]

    def test_user_signin_success(self, api_client):
        """Test successful user signin"""
        # Create user
        user_data = data_factory.generate_user(role="STUDENT")
        api_client.signup(user_data)

        # Sign in
        credentials = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        response = api_client.signin(credentials)

        assert response.status_code == 200
        user = response.json()
        assert user["username"] == user_data["username"]
        assert user["role"] == "STUDENT"
        assert api_client.current_user is not None

    def test_user_signin_wrong_password(self, api_client):
        """Test signin with wrong password fails"""
        # Create user
        user_data = data_factory.generate_user()
        api_client.signup(user_data)

        # Try to sign in with wrong password
        credentials = {
            "username": user_data["username"],
            "password": "wrong_password"
        }
        response = api_client.signin(credentials)

        assert response.status_code in [401, 403]  # Unauthorized

    def test_user_signin_nonexistent_user(self, api_client):
        """Test signin with non-existent user fails"""
        credentials = {
            "username": "nonexistent_user_12345",
            "password": "password123"
        }
        response = api_client.signin(credentials)

        assert response.status_code in [401, 404]  # Unauthorized or not found

    def test_user_signout(self, api_client):
        """Test user signout"""
        # Create and sign in user
        user_data = data_factory.generate_user()
        api_client.signup(user_data)
        api_client.signin({
            "username": user_data["username"],
            "password": user_data["password"]
        })

        # Sign out
        response = api_client.signout()
        assert response.status_code == 200
        assert api_client.current_user is None

    def test_get_profile_authenticated(self, authenticated_client_student):
        """Test getting profile when authenticated"""
        response = authenticated_client_student.get_profile()

        assert response.status_code == 200
        user = response.json()
        assert "username" in user
        assert "role" in user
        assert user["role"] == "STUDENT"

    def test_get_profile_unauthenticated(self, api_client):
        """Test getting profile when not authenticated"""
        response = api_client.get_profile()

        # Should return 401 or return null/empty
        assert response.status_code in [200, 401]
        if response.status_code == 200:
            # If 200, the response should indicate no user
            data = response.json()
            assert data is None or data == {} or "error" in str(data).lower()

    def test_session_persistence(self, api_client):
        """Test that session persists across requests"""
        # Create and sign in user
        user_data = data_factory.generate_user()
        api_client.signup(user_data)
        signin_response = api_client.signin({
            "username": user_data["username"],
            "password": user_data["password"]
        })
        assert signin_response.status_code == 200

        # Make another request using the same client (session should persist)
        profile_response = api_client.get_profile()
        assert profile_response.status_code == 200
        profile = profile_response.json()
        assert profile["username"] == user_data["username"]

    def test_signup_different_roles(self, api_client):
        """Test signup with different user roles"""
        roles = ["STUDENT", "FACULTY", "ADMIN", "TA", "USER"]

        for role in roles:
            user_data = data_factory.generate_user(role=role)
            response = api_client.signup(user_data)

            assert response.status_code == 200
            created_user = response.json()
            assert created_user["role"] == role

    def test_signin_after_signout(self, api_client):
        """Test that user can sign in again after signing out"""
        # Create user
        user_data = data_factory.generate_user()
        api_client.signup(user_data)

        # Sign in
        credentials = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        response1 = api_client.signin(credentials)
        assert response1.status_code == 200

        # Sign out
        api_client.signout()

        # Sign in again
        response2 = api_client.signin(credentials)
        assert response2.status_code == 200
        assert response2.json()["username"] == user_data["username"]
