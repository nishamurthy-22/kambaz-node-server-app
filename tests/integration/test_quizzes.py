"""
Quiz Management Tests
Tests for quiz CRUD operations and question types
"""

import pytest
from helpers.fixtures import data_factory


@pytest.mark.integration
@pytest.mark.quiz
class TestQuizzes:
    """Test suite for quiz management endpoints"""

    def test_create_quiz(self, authenticated_client_faculty, sample_course):
        """Test creating a quiz for a course"""
        course_id = sample_course["_id"]
        quiz_data = data_factory.generate_quiz(course_id)

        response = authenticated_client_faculty.create_quiz(course_id, quiz_data)

        assert response.status_code == 200
        created_quiz = response.json()
        assert created_quiz["title"] == quiz_data["title"]
        assert created_quiz["course"] == course_id
        assert created_quiz["points"] == quiz_data["points"]
        assert "_id" in created_quiz

    def test_create_quiz_with_multiple_choice_questions(self, authenticated_client_faculty, sample_course):
        """Test creating a quiz with multiple choice questions"""
        course_id = sample_course["_id"]

        quiz_data = data_factory.generate_quiz(course_id)
        quiz_data["questions"] = [
            data_factory.generate_multiple_choice_question(
                question="What is 2 + 2?",
                choices=["3", "4", "5", "6"],
                correctChoice=1,
                points=5
            ),
            data_factory.generate_multiple_choice_question(
                question="What is the capital of France?",
                choices=["London", "Berlin", "Paris", "Madrid"],
                correctChoice=2,
                points=5
            )
        ]

        response = authenticated_client_faculty.create_quiz(course_id, quiz_data)

        assert response.status_code == 200
        created_quiz = response.json()
        assert len(created_quiz["questions"]) == 2
        assert created_quiz["questions"][0]["type"] == "MULTIPLE_CHOICE"
        assert created_quiz["questions"][0]["correctChoice"] == 1
        assert created_quiz["questions"][1]["correctChoice"] == 2

    def test_create_quiz_with_true_false_questions(self, authenticated_client_faculty, sample_course):
        """Test creating a quiz with true/false questions"""
        course_id = sample_course["_id"]

        quiz_data = data_factory.generate_quiz(course_id)
        quiz_data["questions"] = [
            data_factory.generate_true_false_question(
                question="Python is a programming language",
                correctAnswer=True
            ),
            data_factory.generate_true_false_question(
                question="The Earth is flat",
                correctAnswer=False
            )
        ]

        response = authenticated_client_faculty.create_quiz(course_id, quiz_data)

        assert response.status_code == 200
        created_quiz = response.json()
        assert len(created_quiz["questions"]) == 2
        assert created_quiz["questions"][0]["type"] == "TRUE_FALSE"
        assert created_quiz["questions"][0]["correctAnswer"] == True
        assert created_quiz["questions"][1]["correctAnswer"] == False

    def test_create_quiz_with_fill_blank_questions(self, authenticated_client_faculty, sample_course):
        """Test creating a quiz with fill in the blank questions"""
        course_id = sample_course["_id"]

        quiz_data = data_factory.generate_quiz(course_id)
        quiz_data["questions"] = [
            data_factory.generate_fill_blank_question(
                question="The capital of France is [blank]",
                blanks=[{
                    "possibleAnswers": ["Paris", "paris"],
                    "caseSensitive": False,
                    "points": 1
                }]
            )
        ]

        response = authenticated_client_faculty.create_quiz(course_id, quiz_data)

        assert response.status_code == 200
        created_quiz = response.json()
        assert len(created_quiz["questions"]) == 1
        assert created_quiz["questions"][0]["type"] == "FILL_BLANK"
        assert len(created_quiz["questions"][0]["blanks"]) == 1

    def test_create_quiz_with_mixed_questions(self, authenticated_client_faculty, sample_course):
        """Test creating a quiz with different question types"""
        course_id = sample_course["_id"]

        quiz_data = data_factory.generate_quiz(course_id)
        quiz_data["questions"] = [
            data_factory.generate_multiple_choice_question(),
            data_factory.generate_true_false_question(),
            data_factory.generate_fill_blank_question()
        ]

        response = authenticated_client_faculty.create_quiz(course_id, quiz_data)

        assert response.status_code == 200
        created_quiz = response.json()
        assert len(created_quiz["questions"]) == 3
        assert created_quiz["questions"][0]["type"] == "MULTIPLE_CHOICE"
        assert created_quiz["questions"][1]["type"] == "TRUE_FALSE"
        assert created_quiz["questions"][2]["type"] == "FILL_BLANK"

    def test_get_quizzes_for_course(self, authenticated_client_faculty, sample_course):
        """Test getting all quizzes for a course"""
        course_id = sample_course["_id"]

        # Create multiple quizzes
        for i in range(3):
            quiz_data = data_factory.generate_quiz(course_id, title=f"Quiz {i+1}")
            authenticated_client_faculty.create_quiz(course_id, quiz_data)

        # Get quizzes
        response = authenticated_client_faculty.get_quizzes(course_id)

        assert response.status_code == 200
        quizzes = response.json()
        assert isinstance(quizzes, list)
        assert len(quizzes) >= 3

    def test_update_quiz(self, authenticated_client_faculty, sample_course):
        """Test updating a quiz"""
        course_id = sample_course["_id"]

        # Create a quiz
        quiz_data = data_factory.generate_quiz(course_id)
        create_response = authenticated_client_faculty.create_quiz(course_id, quiz_data)
        quiz = create_response.json()
        quiz_id = quiz["_id"]

        # Update the quiz
        update_data = {
            "title": "Updated Quiz Title",
            "points": 150,
            "timeLimit": 30
        }
        response = authenticated_client_faculty.update_quiz(quiz_id, update_data)

        assert response.status_code == 200
        updated_quiz = response.json()
        assert updated_quiz["title"] == "Updated Quiz Title"
        assert updated_quiz["points"] == 150
        assert updated_quiz["timeLimit"] == 30

    def test_delete_quiz(self, authenticated_client_faculty, sample_course):
        """Test deleting a quiz"""
        course_id = sample_course["_id"]

        # Create a quiz
        quiz_data = data_factory.generate_quiz(course_id)
        create_response = authenticated_client_faculty.create_quiz(course_id, quiz_data)
        quiz = create_response.json()
        quiz_id = quiz["_id"]

        # Delete the quiz
        response = authenticated_client_faculty.delete_quiz(quiz_id)

        assert response.status_code == 200

    def test_student_view_quiz_no_correct_answers(self, api_client):
        """Test that students don't see correct answers in quiz"""
        # Create faculty and course
        faculty_data = data_factory.generate_user(role="FACULTY")
        api_client.signup(faculty_data)
        api_client.signin({"username": faculty_data["username"], "password": faculty_data["password"]})

        course_data = data_factory.generate_course()
        course = api_client.create_course(course_data).json()

        # Faculty creates quiz with questions
        quiz_data = data_factory.generate_quiz(course["_id"])
        quiz_data["questions"] = [
            data_factory.generate_multiple_choice_question(
                question="What is 2 + 2?",
                choices=["3", "4", "5", "6"],
                correctChoice=1
            )
        ]
        quiz = api_client.create_quiz(course["_id"], quiz_data).json()

        # Create student, enroll and get quizzes
        api_client.signout()
        student_data = data_factory.generate_user(role="STUDENT")
        api_client.signup(student_data)
        api_client.signin({"username": student_data["username"], "password": student_data["password"]})
        api_client.enroll_in_course(course["_id"], "current")

        student_response = api_client.get_quizzes(course["_id"])

        assert student_response.status_code == 200
        student_quizzes = student_response.json()

        # Find the created quiz
        student_quiz = next((q for q in student_quizzes if q["_id"] == quiz["_id"]), None)
        assert student_quiz is not None

        # Check that correct answers are stripped
        if len(student_quiz.get("questions", [])) > 0:
            question = student_quiz["questions"][0]
            # correctChoice should not be present or be null/undefined
            assert "correctChoice" not in question or question.get("correctChoice") is None

    def test_faculty_view_quiz_with_correct_answers(self, authenticated_client_faculty, sample_course):
        """Test that faculty see correct answers in quiz"""
        course_id = sample_course["_id"]

        # Create quiz with questions
        quiz_data = data_factory.generate_quiz(course_id)
        quiz_data["questions"] = [
            data_factory.generate_multiple_choice_question(
                question="What is 2 + 2?",
                choices=["3", "4", "5", "6"],
                correctChoice=1
            )
        ]
        create_response = authenticated_client_faculty.create_quiz(course_id, quiz_data)

        # Get quizzes as faculty
        response = authenticated_client_faculty.get_quizzes(course_id)

        assert response.status_code == 200
        quizzes = response.json()
        assert len(quizzes) >= 1

        # Faculty should see correct answers
        quiz = quizzes[0]
        if len(quiz.get("questions", [])) > 0:
            question = quiz["questions"][0]
            # correctChoice should be present for faculty
            assert "correctChoice" in question
            assert question["correctChoice"] == 1

    def test_quiz_settings(self, authenticated_client_faculty, sample_course):
        """Test creating quiz with various settings"""
        course_id = sample_course["_id"]

        quiz_data = data_factory.generate_quiz(
            course_id,
            published=True,
            shuffleAnswers=True,
            hasTimeLimit=True,
            timeLimit=30,
            multipleAttempts=True,
            attemptsAllowed=3,
            oneQuestionAtATime=True,
            webcamRequired=False
        )

        response = authenticated_client_faculty.create_quiz(course_id, quiz_data)

        assert response.status_code == 200
        quiz = response.json()
        assert quiz["published"] == True
        assert quiz["shuffleAnswers"] == True
        assert quiz["hasTimeLimit"] == True
        assert quiz["timeLimit"] == 30
        assert quiz["multipleAttempts"] == True
        assert quiz["attemptsAllowed"] == 3
        assert quiz["oneQuestionAtATime"] == True
        assert quiz["webcamRequired"] == False

    def test_debug_quiz_endpoint_faculty(self, authenticated_client_faculty, sample_course):
        """Test debug quiz endpoint for faculty"""
        course_id = sample_course["_id"]

        # Create a quiz
        quiz_data = data_factory.generate_quiz(course_id)
        quiz_data["questions"] = [
            data_factory.generate_multiple_choice_question()
        ]
        create_response = authenticated_client_faculty.create_quiz(course_id, quiz_data)
        quiz = create_response.json()

        # Debug endpoint
        response = authenticated_client_faculty.debug_quiz(quiz["_id"])

        assert response.status_code == 200
        debug_quiz = response.json()
        assert "_id" in debug_quiz
        # Debug should show all quiz data including correct answers

    def test_student_cannot_access_debug_endpoint(self, authenticated_client_student, authenticated_client_faculty, sample_course):
        """Test that students cannot access debug quiz endpoint"""
        course_id = sample_course["_id"]

        # Faculty creates quiz
        quiz_data = data_factory.generate_quiz(course_id)
        create_response = authenticated_client_faculty.create_quiz(course_id, quiz_data)
        quiz = create_response.json()

        # Student tries to access debug endpoint
        response = authenticated_client_student.debug_quiz(quiz["_id"])

        # Should fail with authorization error
        assert response.status_code in [401, 403, 500]
