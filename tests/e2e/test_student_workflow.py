"""
Student Workflow E2E Tests
Complete end-to-end tests for student user journeys
"""

import pytest
from helpers.fixtures import data_factory
from helpers.api_client import APIClient


@pytest.mark.e2e
class TestStudentWorkflow:
    """End-to-end test suite for student workflows"""

    def test_complete_student_journey(self, api_client):
        """
        Test complete student journey:
        1. Signup
        2. Login
        3. Browse courses
        4. Enroll in course
        5. View modules and assignments
        6. Take a quiz
        7. Submit quiz
        8. View results
        9. Logout
        """
        # 1. Create a faculty and course first
        faculty_data = data_factory.generate_user(role="FACULTY")
        api_client.signup(faculty_data)
        api_client.signin({
            "username": faculty_data["username"],
            "password": faculty_data["password"]
        })

        course_data = data_factory.generate_course(name="Introduction to Python")
        course_response = api_client.create_course(course_data)
        course = course_response.json()
        course_id = course["_id"]

        # Create a module
        module_data = data_factory.generate_module(course_id, name="Week 1: Basics")
        api_client.create_module(course_id, module_data)

        # Create an assignment
        assignment_data = data_factory.generate_assignment(course_id, title="Assignment 1")
        api_client.create_assignment(course_id, assignment_data)

        # Create a quiz
        quiz_data = data_factory.generate_quiz(course_id, title="Quiz 1")
        quiz_data["questions"] = [
            data_factory.generate_multiple_choice_question(
                question="What is Python?",
                choices=["A snake", "A programming language", "A type of car", "A food"],
                correctChoice=1,
                points=10
            ),
            data_factory.generate_true_false_question(
                question="Python is easy to learn",
                correctAnswer=True,
                points=5
            )
        ]
        quiz_response = api_client.create_quiz(course_id, quiz_data)
        quiz = quiz_response.json()

        api_client.signout()

        # 2. Student signup
        student_data = data_factory.generate_user(role="STUDENT")
        signup_response = api_client.signup(student_data)
        assert signup_response.status_code == 200

        # 3. Student login
        signin_response = api_client.signin({
            "username": student_data["username"],
            "password": student_data["password"]
        })
        assert signin_response.status_code == 200

        # 4. Browse all courses
        courses_response = api_client.get_courses()
        assert courses_response.status_code == 200
        courses = courses_response.json()
        assert len(courses) >= 1

        # 5. Enroll in the course
        enroll_response = api_client.enroll_in_course(course_id, "current")
        assert enroll_response.status_code == 200

        # 6. View my enrollments
        enrollments_response = api_client.get_enrollments()
        assert enrollments_response.status_code == 200
        enrollments = enrollments_response.json()
        assert len(enrollments) >= 1

        # 7. View course modules
        modules_response = api_client.get_modules(course_id)
        assert modules_response.status_code == 200
        modules = modules_response.json()
        assert len(modules) >= 1

        # 8. View course assignments
        assignments_response = api_client.get_assignments(course_id)
        assert assignments_response.status_code == 200
        assignments = assignments_response.json()
        assert len(assignments) >= 1

        # 9. View course quizzes
        quizzes_response = api_client.get_quizzes(course_id)
        assert quizzes_response.status_code == 200
        quizzes = quizzes_response.json()
        assert len(quizzes) >= 1

        # 10. Start quiz attempt
        start_attempt_response = api_client.start_quiz_attempt(quiz["_id"])
        assert start_attempt_response.status_code == 200
        attempt = start_attempt_response.json()
        assert attempt["inProgress"] == True

        # 11. Submit quiz answers
        answers = [
            {"question": quiz["questions"][0]["_id"], "answer": 1},  # Correct
            {"question": quiz["questions"][1]["_id"], "answer": True}  # Correct
        ]
        submit_response = api_client.submit_attempt(attempt["_id"], answers)
        assert submit_response.status_code == 200
        submitted_attempt = submit_response.json()
        assert submitted_attempt["inProgress"] == False
        assert submitted_attempt["score"] == 15  # 10 + 5

        # 12. View quiz results
        latest_attempt_response = api_client.get_latest_attempt(quiz["_id"])
        assert latest_attempt_response.status_code == 200
        latest = latest_attempt_response.json()
        assert latest["score"] == 15

        # 13. Logout
        signout_response = api_client.signout()
        assert signout_response.status_code == 200

    def test_student_multiple_quiz_attempts(self, api_client):
        """Test student taking multiple quiz attempts"""
        # Setup: Create faculty, course, and quiz
        faculty_data = data_factory.generate_user(role="FACULTY")
        api_client.signup(faculty_data)
        api_client.signin({
            "username": faculty_data["username"],
            "password": faculty_data["password"]
        })

        course_data = data_factory.generate_course()
        course_response = api_client.create_course(course_data)
        course = course_response.json()

        quiz_data = data_factory.generate_quiz(
            course["_id"],
            multipleAttempts=True,
            attemptsAllowed=3
        )
        quiz_data["questions"] = [
            data_factory.generate_multiple_choice_question(
                question="Test question",
                choices=["A", "B", "C", "D"],
                correctChoice=1,
                points=10
            )
        ]
        quiz_response = api_client.create_quiz(course["_id"], quiz_data)
        quiz = quiz_response.json()

        api_client.signout()

        # Student takes quiz multiple times
        student_data = data_factory.generate_user(role="STUDENT")
        api_client.signup(student_data)
        api_client.signin({
            "username": student_data["username"],
            "password": student_data["password"]
        })

        api_client.enroll_in_course(course["_id"], "current")

        # Attempt 1: Wrong answer
        attempt1 = api_client.start_quiz_attempt(quiz["_id"]).json()
        submit1 = api_client.submit_attempt(
            attempt1["_id"],
            [{"question": quiz["questions"][0]["_id"], "answer": 0}]  # Wrong
        ).json()
        assert submit1["score"] == 0

        # Attempt 2: Correct answer
        attempt2 = api_client.start_quiz_attempt(quiz["_id"]).json()
        submit2 = api_client.submit_attempt(
            attempt2["_id"],
            [{"question": quiz["questions"][0]["_id"], "answer": 1}]  # Correct
        ).json()
        assert submit2["score"] == 10

        # Check attempt count
        count_response = api_client.get_attempt_count(quiz["_id"])
        assert count_response.status_code == 200
        assert count_response.json()["count"] == 2

    def test_student_cannot_see_correct_answers(self, api_client):
        """Test that students don't see correct answers before submitting"""
        # Setup faculty and course
        faculty_data = data_factory.generate_user(role="FACULTY")
        api_client.signup(faculty_data)
        api_client.signin({
            "username": faculty_data["username"],
            "password": faculty_data["password"]
        })

        course_data = data_factory.generate_course()
        course = api_client.create_course(course_data).json()

        quiz_data = data_factory.generate_quiz(course["_id"])
        quiz_data["questions"] = [
            data_factory.generate_multiple_choice_question(
                question="Secret question",
                choices=["A", "B", "C", "D"],
                correctChoice=2
            )
        ]
        quiz = api_client.create_quiz(course["_id"], quiz_data).json()

        api_client.signout()

        # Student views quiz
        student_data = data_factory.generate_user(role="STUDENT")
        api_client.signup(student_data)
        api_client.signin({
            "username": student_data["username"],
            "password": student_data["password"]
        })

        api_client.enroll_in_course(course["_id"], "current")

        quizzes_response = api_client.get_quizzes(course["_id"])
        quizzes = quizzes_response.json()

        student_quiz = next((q for q in quizzes if q["_id"] == quiz["_id"]), None)
        assert student_quiz is not None

        # Verify correct answers are hidden
        if len(student_quiz.get("questions", [])) > 0:
            question = student_quiz["questions"][0]
            assert "correctChoice" not in question or question.get("correctChoice") is None
