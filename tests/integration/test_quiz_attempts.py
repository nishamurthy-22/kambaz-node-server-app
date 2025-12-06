"""
Quiz Attempt Tests
Tests for quiz submission, grading, and attempt management
"""

import pytest
from helpers.fixtures import data_factory


@pytest.mark.integration
@pytest.mark.quiz
class TestQuizAttempts:
    """Test suite for quiz attempt endpoints"""

    def setup_quiz_with_questions(self, authenticated_client_faculty, course_id):
        """Helper to create a quiz with sample questions"""
        quiz_data = data_factory.generate_quiz(course_id)
        quiz_data["questions"] = [
            data_factory.generate_multiple_choice_question(
                question="What is 2 + 2?",
                choices=["3", "4", "5", "6"],
                correctChoice=1,
                points=10
            ),
            data_factory.generate_true_false_question(
                question="Python is a programming language",
                correctAnswer=True,
                points=5
            ),
            data_factory.generate_fill_blank_question(
                question="The capital of France is [blank]",
                blanks=[{
                    "possibleAnswers": ["Paris", "paris"],
                    "caseSensitive": False,
                    "points": 5
                }],
                points=5
            )
        ]
        response = authenticated_client_faculty.create_quiz(course_id, quiz_data)
        return response.json()

    def test_start_quiz_attempt(self, authenticated_client_student, authenticated_client_faculty, sample_course):
        """Test starting a new quiz attempt"""
        course_id = sample_course["_id"]

        # Faculty creates quiz
        quiz = self.setup_quiz_with_questions(authenticated_client_faculty, course_id)

        # Student enrolls and starts attempt
        authenticated_client_student.enroll_in_course(course_id, "current")
        response = authenticated_client_student.start_quiz_attempt(quiz["_id"])

        assert response.status_code == 200
        attempt = response.json()
        assert attempt["quiz"] == quiz["_id"]
        assert attempt["inProgress"] == True
        assert "attemptNumber" in attempt
        assert "_id" in attempt

    def test_get_in_progress_attempt(self, authenticated_client_student, authenticated_client_faculty, sample_course):
        """Test getting in-progress attempt"""
        course_id = sample_course["_id"]

        # Setup quiz and start attempt
        quiz = self.setup_quiz_with_questions(authenticated_client_faculty, course_id)
        authenticated_client_student.enroll_in_course(course_id, "current")
        start_response = authenticated_client_student.start_quiz_attempt(quiz["_id"])
        started_attempt = start_response.json()

        # Get in-progress attempt
        response = authenticated_client_student.get_in_progress_attempt(quiz["_id"])

        assert response.status_code == 200
        attempt = response.json()
        assert attempt["_id"] == started_attempt["_id"]
        assert attempt["inProgress"] == True

    def test_update_attempt_answers(self, authenticated_client_student, authenticated_client_faculty, sample_course):
        """Test updating attempt answers while in progress"""
        course_id = sample_course["_id"]

        # Setup quiz and start attempt
        quiz = self.setup_quiz_with_questions(authenticated_client_faculty, course_id)
        authenticated_client_student.enroll_in_course(course_id, "current")
        start_response = authenticated_client_student.start_quiz_attempt(quiz["_id"])
        attempt = start_response.json()

        # Update answers
        answers = [
            {"question": quiz["questions"][0]["_id"], "answer": 1},
            {"question": quiz["questions"][1]["_id"], "answer": True}
        ]
        response = authenticated_client_student.update_attempt(attempt["_id"], answers)

        assert response.status_code == 200
        updated_attempt = response.json()
        assert len(updated_attempt["answers"]) == 2

    def test_submit_quiz_attempt_multiple_choice(self, authenticated_client_student, authenticated_client_faculty, sample_course):
        """Test submitting quiz with multiple choice question"""
        course_id = sample_course["_id"]

        # Create simple quiz with one MC question
        quiz_data = data_factory.generate_quiz(course_id)
        quiz_data["questions"] = [
            data_factory.generate_multiple_choice_question(
                question="What is 2 + 2?",
                choices=["3", "4", "5", "6"],
                correctChoice=1,  # Index 1 = "4"
                points=10
            )
        ]
        quiz_response = authenticated_client_faculty.create_quiz(course_id, quiz_data)
        quiz = quiz_response.json()

        # Student starts and submits attempt
        authenticated_client_student.enroll_in_course(course_id, "current")
        start_response = authenticated_client_student.start_quiz_attempt(quiz["_id"])
        attempt = start_response.json()

        # Submit with correct answer
        answers = [
            {"question": quiz["questions"][0]["_id"], "answer": 1}
        ]
        response = authenticated_client_student.submit_attempt(attempt["_id"], answers)

        assert response.status_code == 200
        submitted_attempt = response.json()
        assert submitted_attempt["inProgress"] == False
        assert submitted_attempt["score"] == 10  # Full points
        assert submitted_attempt["answers"][0]["correct"] == True

    def test_submit_quiz_attempt_true_false(self, authenticated_client_student, authenticated_client_faculty, sample_course):
        """Test submitting quiz with true/false question"""
        course_id = sample_course["_id"]

        # Create quiz with T/F question
        quiz_data = data_factory.generate_quiz(course_id)
        quiz_data["questions"] = [
            data_factory.generate_true_false_question(
                question="Python is a programming language",
                correctAnswer=True,
                points=5
            )
        ]
        quiz_response = authenticated_client_faculty.create_quiz(course_id, quiz_data)
        quiz = quiz_response.json()

        # Student submits attempt
        authenticated_client_student.enroll_in_course(course_id, "current")
        start_response = authenticated_client_student.start_quiz_attempt(quiz["_id"])
        attempt = start_response.json()

        answers = [
            {"question": quiz["questions"][0]["_id"], "answer": True}
        ]
        response = authenticated_client_student.submit_attempt(attempt["_id"], answers)

        assert response.status_code == 200
        submitted_attempt = response.json()
        assert submitted_attempt["score"] == 5
        assert submitted_attempt["answers"][0]["correct"] == True

    def test_submit_quiz_attempt_fill_blank(self, authenticated_client_student, authenticated_client_faculty, sample_course):
        """Test submitting quiz with fill in the blank question"""
        course_id = sample_course["_id"]

        # Create quiz with fill blank question
        quiz_data = data_factory.generate_quiz(course_id)
        quiz_data["questions"] = [
            data_factory.generate_fill_blank_question(
                question="The capital of France is [blank]",
                blanks=[{
                    "possibleAnswers": ["Paris", "paris"],
                    "caseSensitive": False,
                    "points": 5
                }],
                points=5
            )
        ]
        quiz_response = authenticated_client_faculty.create_quiz(course_id, quiz_data)
        quiz = quiz_response.json()

        # Student submits attempt
        authenticated_client_student.enroll_in_course(course_id, "current")
        start_response = authenticated_client_student.start_quiz_attempt(quiz["_id"])
        attempt = start_response.json()

        # Submit with correct answer (lowercase)
        answers = [
            {"question": quiz["questions"][0]["_id"], "answer": ["paris"]}
        ]
        response = authenticated_client_student.submit_attempt(attempt["_id"], answers)

        assert response.status_code == 200
        submitted_attempt = response.json()
        assert submitted_attempt["score"] == 5
        assert submitted_attempt["answers"][0]["correct"] == True

    def test_submit_quiz_with_incorrect_answers(self, authenticated_client_student, authenticated_client_faculty, sample_course):
        """Test server-side grading with incorrect answers"""
        course_id = sample_course["_id"]

        # Create quiz
        quiz_data = data_factory.generate_quiz(course_id)
        quiz_data["questions"] = [
            data_factory.generate_multiple_choice_question(
                question="What is 2 + 2?",
                choices=["3", "4", "5", "6"],
                correctChoice=1,  # Correct = index 1
                points=10
            )
        ]
        quiz_response = authenticated_client_faculty.create_quiz(course_id, quiz_data)
        quiz = quiz_response.json()

        # Student submits with wrong answer
        authenticated_client_student.enroll_in_course(course_id, "current")
        start_response = authenticated_client_student.start_quiz_attempt(quiz["_id"])
        attempt = start_response.json()

        answers = [
            {"question": quiz["questions"][0]["_id"], "answer": 0}  # Wrong answer
        ]
        response = authenticated_client_student.submit_attempt(attempt["_id"], answers)

        assert response.status_code == 200
        submitted_attempt = response.json()
        assert submitted_attempt["score"] == 0
        assert submitted_attempt["answers"][0]["correct"] == False

    def test_get_all_attempts_for_quiz(self, authenticated_client_student, authenticated_client_faculty, sample_course):
        """Test getting all attempts for a quiz"""
        course_id = sample_course["_id"]

        # Setup and submit attempt
        quiz = self.setup_quiz_with_questions(authenticated_client_faculty, course_id)
        authenticated_client_student.enroll_in_course(course_id, "current")

        start_response = authenticated_client_student.start_quiz_attempt(quiz["_id"])
        attempt = start_response.json()

        answers = [
            {"question": quiz["questions"][0]["_id"], "answer": 1}
        ]
        authenticated_client_student.submit_attempt(attempt["_id"], answers)

        # Get all attempts
        response = authenticated_client_student.get_quiz_attempts(quiz["_id"])

        assert response.status_code == 200
        attempts = response.json()
        assert isinstance(attempts, list)
        assert len(attempts) >= 1

    def test_get_attempt_count(self, authenticated_client_student, authenticated_client_faculty, sample_course):
        """Test getting completed attempt count"""
        course_id = sample_course["_id"]

        # Setup and submit attempt
        quiz = self.setup_quiz_with_questions(authenticated_client_faculty, course_id)
        authenticated_client_student.enroll_in_course(course_id, "current")

        start_response = authenticated_client_student.start_quiz_attempt(quiz["_id"])
        attempt = start_response.json()

        answers = [{"question": quiz["questions"][0]["_id"], "answer": 1}]
        authenticated_client_student.submit_attempt(attempt["_id"], answers)

        # Get count
        response = authenticated_client_student.get_attempt_count(quiz["_id"])

        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 1

    def test_get_latest_attempt(self, authenticated_client_student, authenticated_client_faculty, sample_course):
        """Test getting latest completed attempt"""
        course_id = sample_course["_id"]

        # Setup and submit attempt
        quiz = self.setup_quiz_with_questions(authenticated_client_faculty, course_id)
        authenticated_client_student.enroll_in_course(course_id, "current")

        start_response = authenticated_client_student.start_quiz_attempt(quiz["_id"])
        attempt = start_response.json()

        answers = [{"question": quiz["questions"][0]["_id"], "answer": 1}]
        submit_response = authenticated_client_student.submit_attempt(attempt["_id"], answers)
        submitted_attempt = submit_response.json()

        # Get latest
        response = authenticated_client_student.get_latest_attempt(quiz["_id"])

        assert response.status_code == 200
        latest = response.json()
        assert latest["_id"] == submitted_attempt["_id"]

    def test_get_specific_attempt(self, authenticated_client_student, authenticated_client_faculty, sample_course):
        """Test getting specific attempt by ID"""
        course_id = sample_course["_id"]

        # Setup and submit attempt
        quiz = self.setup_quiz_with_questions(authenticated_client_faculty, course_id)
        authenticated_client_student.enroll_in_course(course_id, "current")

        start_response = authenticated_client_student.start_quiz_attempt(quiz["_id"])
        attempt = start_response.json()

        answers = [{"question": quiz["questions"][0]["_id"], "answer": 1}]
        authenticated_client_student.submit_attempt(attempt["_id"], answers)

        # Get specific attempt
        response = authenticated_client_student.get_attempt(attempt["_id"])

        assert response.status_code == 200
        retrieved_attempt = response.json()
        assert retrieved_attempt["_id"] == attempt["_id"]

    def test_multiple_attempts_if_allowed(self, authenticated_client_student, authenticated_client_faculty, sample_course):
        """Test multiple attempts when allowed"""
        course_id = sample_course["_id"]

        # Create quiz with multiple attempts allowed
        quiz_data = data_factory.generate_quiz(
            course_id,
            multipleAttempts=True,
            attemptsAllowed=3
        )
        quiz_data["questions"] = [
            data_factory.generate_multiple_choice_question(points=10)
        ]
        quiz_response = authenticated_client_faculty.create_quiz(course_id, quiz_data)
        quiz = quiz_response.json()

        authenticated_client_student.enroll_in_course(course_id, "current")

        # Submit first attempt
        start1 = authenticated_client_student.start_quiz_attempt(quiz["_id"])
        attempt1 = start1.json()
        answers = [{"question": quiz["questions"][0]["_id"], "answer": 0}]
        authenticated_client_student.submit_attempt(attempt1["_id"], answers)

        # Submit second attempt
        start2 = authenticated_client_student.start_quiz_attempt(quiz["_id"])
        attempt2 = start2.json()
        authenticated_client_student.submit_attempt(attempt2["_id"], answers)

        # Verify attempt numbers
        assert attempt1["attemptNumber"] == 1
        assert attempt2["attemptNumber"] == 2

    def test_case_sensitive_fill_blank(self, authenticated_client_student, authenticated_client_faculty, sample_course):
        """Test case sensitivity in fill in the blank questions"""
        course_id = sample_course["_id"]

        # Create quiz with case-sensitive fill blank
        quiz_data = data_factory.generate_quiz(course_id)
        quiz_data["questions"] = [
            {
                "type": "FILL_BLANK",
                "title": "Case Sensitive Question",
                "points": 5,
                "question": "The programming language is [blank]",
                "blanks": [{
                    "possibleAnswers": ["Python"],
                    "caseSensitive": True,
                    "points": 5
                }]
            }
        ]
        quiz_response = authenticated_client_faculty.create_quiz(course_id, quiz_data)
        quiz = quiz_response.json()

        authenticated_client_student.enroll_in_course(course_id, "current")

        # Submit with wrong case
        start_response = authenticated_client_student.start_quiz_attempt(quiz["_id"])
        attempt = start_response.json()

        answers = [
            {"question": quiz["questions"][0]["_id"], "answer": ["python"]}  # Wrong case
        ]
        response = authenticated_client_student.submit_attempt(attempt["_id"], answers)

        assert response.status_code == 200
        submitted_attempt = response.json()
        # Should be marked incorrect due to case sensitivity
        assert submitted_attempt["score"] == 0
