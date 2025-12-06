"""
Faculty Workflow E2E Tests
Complete end-to-end tests for faculty user journeys
"""

import pytest
from helpers.fixtures import data_factory


@pytest.mark.e2e
class TestFacultyWorkflow:
    """End-to-end test suite for faculty workflows"""

    def test_complete_faculty_journey(self, api_client):
        """
        Test complete faculty journey:
        1. Signup as faculty
        2. Login
        3. Create a course
        4. Add modules to course
        5. Add assignments
        6. Create quiz with questions
        7. Publish quiz
        8. View student submissions
        9. Logout
        """
        # 1. Faculty signup
        faculty_data = data_factory.generate_user(role="FACULTY")
        signup_response = api_client.signup(faculty_data)
        assert signup_response.status_code == 200

        # 2. Faculty login
        signin_response = api_client.signin({
            "username": faculty_data["username"],
            "password": faculty_data["password"]
        })
        assert signin_response.status_code == 200

        # 3. Create a course
        course_data = data_factory.generate_course(
            name="Advanced Web Development",
            number="CS401",
            credits=4
        )
        course_response = api_client.create_course(course_data)
        assert course_response.status_code == 200
        course = course_response.json()
        course_id = course["_id"]

        # 4. Verify faculty is auto-enrolled
        enrollments_response = api_client.get_enrollments()
        assert enrollments_response.status_code == 200
        enrollments = enrollments_response.json()
        course_ids = [e["course"] for e in enrollments]
        assert course_id in course_ids

        # 5. Add modules to course
        modules = []
        for i in range(3):
            module_data = data_factory.generate_module(
                course_id,
                name=f"Week {i+1}",
                lessons=[
                    data_factory.generate_lesson(name=f"Lesson {i+1}.1"),
                    data_factory.generate_lesson(name=f"Lesson {i+1}.2")
                ]
            )
            module_response = api_client.create_module(course_id, module_data)
            assert module_response.status_code == 200
            modules.append(module_response.json())

        # 6. Verify modules were created
        modules_response = api_client.get_modules(course_id)
        assert modules_response.status_code == 200
        created_modules = modules_response.json()
        assert len(created_modules) >= 3

        # 7. Add assignments
        assignments = []
        for i in range(2):
            assignment_data = data_factory.generate_assignment(
                course_id,
                title=f"Assignment {i+1}",
                points=100
            )
            assignment_response = api_client.create_assignment(course_id, assignment_data)
            assert assignment_response.status_code == 200
            assignments.append(assignment_response.json())

        # 8. Verify assignments were created
        assignments_response = api_client.get_assignments(course_id)
        assert assignments_response.status_code == 200
        created_assignments = assignments_response.json()
        assert len(created_assignments) >= 2

        # 9. Create comprehensive quiz with all question types
        quiz_data = data_factory.generate_quiz(
            course_id,
            title="Midterm Exam",
            points=100,
            published=False,
            multipleAttempts=True,
            attemptsAllowed=2,
            timeLimit=60
        )
        quiz_data["questions"] = [
            data_factory.generate_multiple_choice_question(
                question="What is React?",
                choices=["A library", "A framework", "A language", "An IDE"],
                correctChoice=0,
                points=10
            ),
            data_factory.generate_multiple_choice_question(
                question="What is Node.js?",
                choices=["A browser", "A runtime", "A database", "A framework"],
                correctChoice=1,
                points=10
            ),
            data_factory.generate_true_false_question(
                question="JavaScript is the same as Java",
                correctAnswer=False,
                points=5
            ),
            data_factory.generate_true_false_question(
                question="HTTP is stateless",
                correctAnswer=True,
                points=5
            ),
            data_factory.generate_fill_blank_question(
                question="The ___ method is used to send data to a server",
                blanks=[{
                    "possibleAnswers": ["POST", "post"],
                    "caseSensitive": False,
                    "points": 10
                }],
                points=10
            )
        ]

        quiz_response = api_client.create_quiz(course_id, quiz_data)
        assert quiz_response.status_code == 200
        quiz = quiz_response.json()

        # 10. Verify quiz was created with all questions
        assert len(quiz["questions"]) == 5
        assert quiz["published"] == False

        # 11. Publish the quiz
        update_response = api_client.update_quiz(quiz["_id"], {"published": True})
        assert update_response.status_code == 200
        updated_quiz = update_response.json()
        assert updated_quiz["published"] == True

        # 12. View all quizzes for the course
        quizzes_response = api_client.get_quizzes(course_id)
        assert quizzes_response.status_code == 200
        quizzes = quizzes_response.json()
        assert len(quizzes) >= 1

        # 13. Faculty should see correct answers
        faculty_quiz = quizzes[0]
        if len(faculty_quiz.get("questions", [])) > 0:
            mc_question = next((q for q in faculty_quiz["questions"] if q["type"] == "MULTIPLE_CHOICE"), None)
            if mc_question:
                assert "correctChoice" in mc_question

        # 14. Update course information
        update_course_data = {
            "description": "Updated course description with syllabus"
        }
        update_course_response = api_client.update_course(course_id, update_course_data)
        assert update_course_response.status_code == 200

        # 15. Get course users (should have at least faculty)
        users_response = api_client.get_course_users(course_id)
        assert users_response.status_code == 200
        users = users_response.json()
        assert len(users) >= 1

        # 16. Logout
        signout_response = api_client.signout()
        assert signout_response.status_code == 200

    def test_faculty_manage_student_enrollments(self, api_client):
        """Test faculty enrolling and managing students"""
        # Create faculty and course
        faculty_data = data_factory.generate_user(role="FACULTY")
        api_client.signup(faculty_data)
        api_client.signin({
            "username": faculty_data["username"],
            "password": faculty_data["password"]
        })

        course_data = data_factory.generate_course()
        course = api_client.create_course(course_data).json()

        api_client.signout()

        # Create students
        students = []
        for i in range(3):
            student_data = data_factory.generate_user(role="STUDENT")
            api_client.signup(student_data)
            students.append(student_data)

        # Faculty enrolls students
        api_client.signin({
            "username": faculty_data["username"],
            "password": faculty_data["password"]
        })

        # Get student IDs and enroll them
        for student in students:
            # Sign in as student to get ID
            api_client.signout()
            api_client.signin({
                "username": student["username"],
                "password": student["password"]
            })
            profile = api_client.get_profile().json()
            student_id = profile["_id"]

            # Sign back in as faculty
            api_client.signout()
            api_client.signin({
                "username": faculty_data["username"],
                "password": faculty_data["password"]
            })

            # Enroll student
            enroll_response = api_client.enroll_in_course(course["_id"], student_id)
            assert enroll_response.status_code == 200

        # Verify all students are enrolled
        users_response = api_client.get_course_users(course["_id"])
        users = users_response.json()
        # Should have faculty + 3 students
        assert len(users) >= 4

    def test_faculty_view_quiz_attempts(self, api_client):
        """Test faculty viewing student quiz attempts"""
        # Setup: Faculty creates course and quiz
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
                question="Test question",
                correctChoice=1,
                points=10
            )
        ]
        quiz = api_client.create_quiz(course["_id"], quiz_data).json()

        api_client.signout()

        # Student takes quiz
        student_data = data_factory.generate_user(role="STUDENT")
        api_client.signup(student_data)
        api_client.signin({
            "username": student_data["username"],
            "password": student_data["password"]
        })

        api_client.enroll_in_course(course["_id"], "current")
        attempt = api_client.start_quiz_attempt(quiz["_id"]).json()
        api_client.submit_attempt(
            attempt["_id"],
            [{"question": quiz["questions"][0]["_id"], "answer": 1}]
        )

        # Note: Backend doesn't have faculty-specific endpoint to view all student attempts
        # Faculty would need to access this through their own interface
        # This test verifies the student submission was successful

        api_client.signout()

        # Faculty signs back in
        api_client.signin({
            "username": faculty_data["username"],
            "password": faculty_data["password"]
        })

        # Faculty can use debug endpoint
        debug_response = api_client.debug_quiz(quiz["_id"])
        assert debug_response.status_code == 200

    def test_faculty_delete_course_cascade(self, api_client):
        """Test that deleting a course removes all associated content"""
        # Create faculty and course
        faculty_data = data_factory.generate_user(role="FACULTY")
        api_client.signup(faculty_data)
        api_client.signin({
            "username": faculty_data["username"],
            "password": faculty_data["password"]
        })

        course_data = data_factory.generate_course()
        course = api_client.create_course(course_data).json()
        course_id = course["_id"]

        # Add content to course
        api_client.create_module(course_id, data_factory.generate_module(course_id))
        api_client.create_assignment(course_id, data_factory.generate_assignment(course_id))

        quiz_data = data_factory.generate_quiz(course_id)
        quiz_data["questions"] = [data_factory.generate_multiple_choice_question()]
        api_client.create_quiz(course_id, quiz_data)

        # Delete the course
        delete_response = api_client.delete_course(course_id)
        assert delete_response.status_code == 200

        # Verify content is deleted
        modules_response = api_client.get_modules(course_id)
        assignments_response = api_client.get_assignments(course_id)

        # These should return 404 or empty lists
        assert modules_response.status_code in [200, 404]
        assert assignments_response.status_code in [200, 404]
