"""
Test Fixtures
Provides factory functions for generating test data
"""

from faker import Faker
from datetime import datetime, timedelta
import uuid
from typing import Dict, List, Optional

fake = Faker()


class DataFactory:
    """Factory class for generating test data"""

    @staticmethod
    def generate_user(role: str = "STUDENT", **kwargs) -> Dict:
        """
        Generate user data

        Args:
            role: User role (STUDENT, FACULTY, ADMIN, TA, USER)
            **kwargs: Override specific fields

        Returns:
            User data dictionary
        """
        first_name = kwargs.get("firstName", fake.first_name())
        last_name = kwargs.get("lastName", fake.last_name())
        username = kwargs.get("username", f"{first_name.lower()}_{last_name.lower()}_{fake.random_number(digits=4)}")

        user = {
            "username": username,
            "password": kwargs.get("password", "password123"),
            "firstName": first_name,
            "lastName": last_name,
            "email": kwargs.get("email", f"{username}@test.com"),
            "role": role,
            "dob": kwargs.get("dob", fake.date_of_birth(minimum_age=18, maximum_age=70).isoformat()),
            "loginId": kwargs.get("loginId", str(uuid.uuid4())),
            "section": kwargs.get("section", fake.random_element(["A", "B", "C"])),
        }

        # Add any additional kwargs
        for key, value in kwargs.items():
            if key not in user:
                user[key] = value

        return user

    @staticmethod
    def generate_course(**kwargs) -> Dict:
        """
        Generate course data

        Args:
            **kwargs: Override specific fields

        Returns:
            Course data dictionary
        """
        course_number = kwargs.get("number", f"CS{fake.random_number(digits=4)}")
        course = {
            "name": kwargs.get("name", f"{fake.catch_phrase()} - {fake.bs().title()}"),
            "number": course_number,
            "credits": kwargs.get("credits", fake.random_int(min=1, max=4)),
            "description": kwargs.get("description", fake.paragraph(nb_sentences=3)),
            "department": kwargs.get("department", fake.random_element(["Computer Science", "Mathematics", "Physics", "Engineering"])),
            "startDate": kwargs.get("startDate", datetime.now().strftime("%Y-%m-%d")),
            "endDate": kwargs.get("endDate", (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")),
        }

        # Add any additional kwargs
        for key, value in kwargs.items():
            if key not in course:
                course[key] = value

        return course

    @staticmethod
    def generate_module(course_id: str, **kwargs) -> Dict:
        """
        Generate module data

        Args:
            course_id: ID of the course
            **kwargs: Override specific fields

        Returns:
            Module data dictionary
        """
        module = {
            "name": kwargs.get("name", f"Module: {fake.catch_phrase()}"),
            "description": kwargs.get("description", fake.paragraph(nb_sentences=2)),
            "course": course_id,
            "lessons": kwargs.get("lessons", [])
        }

        # Add any additional kwargs
        for key, value in kwargs.items():
            if key not in module:
                module[key] = value

        return module

    @staticmethod
    def generate_lesson(**kwargs) -> Dict:
        """
        Generate lesson data

        Args:
            **kwargs: Override specific fields

        Returns:
            Lesson data dictionary
        """
        lesson = {
            "name": kwargs.get("name", f"Lesson: {fake.sentence(nb_words=4)}"),
            "description": kwargs.get("description", fake.paragraph(nb_sentences=1)),
        }

        # Add any additional kwargs
        for key, value in kwargs.items():
            if key not in lesson:
                lesson[key] = value

        return lesson

    @staticmethod
    def generate_assignment(course_id: str, **kwargs) -> Dict:
        """
        Generate assignment data

        Args:
            course_id: ID of the course
            **kwargs: Override specific fields

        Returns:
            Assignment data dictionary
        """
        assignment = {
            "title": kwargs.get("title", f"Assignment: {fake.sentence(nb_words=5)}"),
            "course": course_id,
            "description": kwargs.get("description", fake.paragraph(nb_sentences=3)),
            "points": kwargs.get("points", fake.random_int(min=10, max=100)),
            "Not available until": kwargs.get("Not available until", datetime.now().strftime("%Y-%m-%d")),
            "Due": kwargs.get("Due", (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")),
            "Available until": kwargs.get("Available until", (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")),
        }

        # Add any additional kwargs
        for key, value in kwargs.items():
            if key not in assignment:
                assignment[key] = value

        return assignment

    @staticmethod
    def generate_quiz(course_id: str, **kwargs) -> Dict:
        """
        Generate quiz data

        Args:
            course_id: ID of the course
            **kwargs: Override specific fields

        Returns:
            Quiz data dictionary
        """
        quiz = {
            "title": kwargs.get("title", f"Quiz: {fake.sentence(nb_words=4)}"),
            "course": course_id,
            "description": kwargs.get("description", fake.paragraph(nb_sentences=2)),
            "points": kwargs.get("points", 100),
            "Available Date": kwargs.get("Available Date", datetime.now().strftime("%Y-%m-%d")),
            "Due Date": kwargs.get("Due Date", (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")),
            "Available Until Date": kwargs.get("Available Until Date", (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")),
            "Questions": kwargs.get("Questions", 10),
            "published": kwargs.get("published", True),
            "quizType": kwargs.get("quizType", "Graded Quiz"),
            "assignmentGroup": kwargs.get("assignmentGroup", "QUIZZES"),
            "shuffleAnswers": kwargs.get("shuffleAnswers", True),
            "hasTimeLimit": kwargs.get("hasTimeLimit", True),
            "timeLimit": kwargs.get("timeLimit", 20),
            "multipleAttempts": kwargs.get("multipleAttempts", False),
            "attemptsAllowed": kwargs.get("attemptsAllowed", 1),
            "showCorrectAnswers": kwargs.get("showCorrectAnswers", "After submission"),
            "accessCode": kwargs.get("accessCode", ""),
            "oneQuestionAtATime": kwargs.get("oneQuestionAtATime", True),
            "webcamRequired": kwargs.get("webcamRequired", False),
            "lockQuestionsAfterAnswering": kwargs.get("lockQuestionsAfterAnswering", False),
            "questions": kwargs.get("questions", [])
        }

        # Add any additional kwargs
        for key, value in kwargs.items():
            if key not in quiz:
                quiz[key] = value

        return quiz

    @staticmethod
    def generate_multiple_choice_question(**kwargs) -> Dict:
        """Generate multiple choice question"""
        choices = kwargs.get("choices", [
            "Option A: " + fake.sentence(),
            "Option B: " + fake.sentence(),
            "Option C: " + fake.sentence(),
            "Option D: " + fake.sentence()
        ])

        question = {
            "type": "MULTIPLE_CHOICE",
            "title": kwargs.get("title", f"Question: {fake.sentence(nb_words=6)}"),
            "points": kwargs.get("points", 1),
            "question": kwargs.get("question", fake.sentence() + "?"),
            "choices": choices,
            "correctChoice": kwargs.get("correctChoice", 0)
        }

        return question

    @staticmethod
    def generate_true_false_question(**kwargs) -> Dict:
        """Generate true/false question"""
        question = {
            "type": "TRUE_FALSE",
            "title": kwargs.get("title", f"Question: {fake.sentence(nb_words=6)}"),
            "points": kwargs.get("points", 1),
            "question": kwargs.get("question", fake.sentence() + "?"),
            "correctAnswer": kwargs.get("correctAnswer", fake.boolean())
        }

        return question

    @staticmethod
    def generate_fill_blank_question(**kwargs) -> Dict:
        """Generate fill in the blank question"""
        question = {
            "type": "FILL_BLANK",
            "title": kwargs.get("title", f"Question: {fake.sentence(nb_words=6)}"),
            "points": kwargs.get("points", 1),
            "question": kwargs.get("question", f"The capital of France is [blank]."),
            "blanks": kwargs.get("blanks", [{
                "possibleAnswers": ["Paris", "paris"],
                "caseSensitive": False,
                "points": 1
            }])
        }

        return question

    @staticmethod
    def generate_enrollment(user_id: str, course_id: str, **kwargs) -> Dict:
        """Generate enrollment data"""
        enrollment = {
            "user": user_id,
            "course": course_id,
            "grade": kwargs.get("grade", fake.random_int(min=0, max=100)),
            "letterGrade": kwargs.get("letterGrade", fake.random_element(["A", "A-", "B+", "B", "B-", "C+", "C", "D", "F"])),
            "status": kwargs.get("status", "ENROLLED")
        }

        return enrollment


# Convenience instances
data_factory = DataFactory()
