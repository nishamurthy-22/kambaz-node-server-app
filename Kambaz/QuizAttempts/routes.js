import QuizAttemptsDao from "./dao.js";
import QuizzesDao from "../Quizzes/dao.js";

export default function QuizAttemptsRoutes(app) {
  const dao = QuizAttemptsDao();
  const quizzesDao = QuizzesDao();

  const gradeQuizAttempt = (quiz, answers) => {
    let totalScore = 0;
    const gradedAnswers = [];

    quiz.questions.forEach((question) => {
      const studentAnswer = answers.find(a => a.question === question._id);
      if (!studentAnswer) {
        gradedAnswers.push({
          question: question._id,
          answer: null,
          correct: false,
          points: 0
        });
        return;
      }

      let isCorrect = false;
      let pointsEarned = 0;

      if (question.type === "MULTIPLE_CHOICE") {
        isCorrect = studentAnswer.answer === question.correctAnswer;
        pointsEarned = isCorrect ? (question.points || 0) : 0;
      } else if (question.type === "TRUE_FALSE") {
        // Handle both boolean and string representations
        const studentAns = studentAnswer.answer;
        const correctAns = question.correctAnswer;
        
        // Normalize both to boolean for comparison
        const studentBool = typeof studentAns === 'boolean' ? studentAns : studentAns === 'true';
        const correctBool = typeof correctAns === 'boolean' ? correctAns : correctAns === 'true';
        
        isCorrect = studentBool === correctBool;
        pointsEarned = isCorrect ? (question.points || 0) : 0;
      } else if (question.type === "FILL_BLANK") {
        if (question.blanks && question.blanks.length > 0) {
          const answersArray = Array.isArray(studentAnswer.answer) ? studentAnswer.answer : [];
          let allCorrect = true;

          question.blanks.forEach((blank, index) => {
            const userAnswer = answersArray[index] || "";
            if (!userAnswer) {
              allCorrect = false;
              return;
            }

            const answerToCheck = blank.caseSensitive ? userAnswer : userAnswer.toLowerCase();
            const blankIsCorrect = blank.possibleAnswers?.some((possibleAnswer) => {
              const checkAnswer = blank.caseSensitive ? possibleAnswer : possibleAnswer.toLowerCase();
              return answerToCheck.trim() === checkAnswer.trim();
            });

            if (blankIsCorrect) {
              pointsEarned += blank.points || 0;
            } else {
              allCorrect = false;
            }
          });

          isCorrect = allCorrect;
        } else {
          const userAnswer = question.caseSensitive ? studentAnswer.answer : studentAnswer.answer.toLowerCase();
          isCorrect = question.possibleAnswers?.some((possibleAnswer) => {
            const checkAnswer = question.caseSensitive ? possibleAnswer : possibleAnswer.toLowerCase();
            return userAnswer.trim() === checkAnswer.trim();
          });
          pointsEarned = isCorrect ? (question.points || 0) : 0;
        }
      }

      totalScore += pointsEarned;
      gradedAnswers.push({
        question: question._id,
        answer: studentAnswer.answer,
        correct: isCorrect,
        points: pointsEarned
      });
    });

    return { score: totalScore, answers: gradedAnswers };
  };

  const startAttempt = async (req, res) => {
    if (req.session["currentUser"]) {
    }
    
    const currentUser = req.session["currentUser"];
    if (!currentUser) {
      res.sendStatus(401);
      return;
    }

    const { quizId } = req.params;
    try {
      const attemptCount = await dao.getCompletedAttemptCount(currentUser._id, quizId);
      
      const newAttempt = {
        quiz: quizId,
        student: currentUser._id,
        attemptNumber: attemptCount + 1,
        answers: [],
        score: 0,
        totalPoints: 0,
        startedAt: new Date(),
        submittedAt: null,
        inProgress: true,
      };
      const attempt = await dao.createAttempt(newAttempt);
      res.json(attempt);
    } catch (error) {
      res.status(500).json({ error: "Failed to start quiz attempt" });
    }
  };

  const updateAttempt = async (req, res) => {
    
    const currentUser = req.session["currentUser"];
    if (!currentUser) {
      res.sendStatus(401);
      return;
    }

    const { attemptId } = req.params;
    try {
      const attempt = await dao.findAttemptById(attemptId);
      if (!attempt) {
        res.status(404).json({ error: "Attempt not found" });
        return;
      }
      if (attempt.student !== currentUser._id) {
        res.sendStatus(403);
        return;
      }
      if (!attempt.inProgress) {
        res.status(400).json({ error: "Cannot update submitted attempt" });
        return;
      }

      const updates = {
        answers: req.body.answers || attempt.answers,
      };
      const updated = await dao.updateAttemptAnswers(attemptId, updates);
      res.json(updated);
    } catch (error) {
      res.status(500).json({ error: "Failed to update quiz attempt" });
    }
  };

  const submitAttempt = async (req, res) => {
    
    const currentUser = req.session["currentUser"];
    if (!currentUser) {
      res.sendStatus(401);
      return;
    }

    const { attemptId } = req.params;
    try {
      const attempt = await dao.findAttemptById(attemptId);
      if (!attempt) {
        res.status(404).json({ error: "Attempt not found" });
        return;
      }
      if (attempt.student !== currentUser._id) {
        res.sendStatus(403);
        return;
      }
      if (!attempt.inProgress) {
        res.status(400).json({ error: "Attempt already submitted" });
        return;
      }

      const quiz = await quizzesDao.findQuizById(attempt.quiz);
      if (!quiz) {
        res.status(404).json({ error: "Quiz not found" });
        return;
      }

      const { score, answers: gradedAnswers } = gradeQuizAttempt(quiz, req.body.answers || []);
      

      const updates = {
        answers: gradedAnswers,
        score: score,
        totalPoints: quiz.points || 0,
        submittedAt: new Date(),
        inProgress: false,
      };
      const submitted = await dao.submitAttempt(attemptId, updates);
      res.json(submitted);
    } catch (error) {
      res.status(500).json({ error: "Failed to submit quiz attempt" });
    }
  };

  const getInProgressAttempt = async (req, res) => {
    if (req.session["currentUser"]) {
    }
    
    const currentUser = req.session["currentUser"];
    if (!currentUser) {
      res.sendStatus(401);
      return;
    }

    const { quizId } = req.params;
    try {
      const attempt = await dao.findInProgressAttempt(currentUser._id, quizId);
      res.json(attempt || null);
    } catch (error) {
      res.status(500).json({ error: "Failed to get in-progress attempt" });
    }
  };

  const getStudentAttempts = async (req, res) => {
    
    const currentUser = req.session["currentUser"];
    if (!currentUser) {
      res.sendStatus(401);
      return;
    }

    const { quizId } = req.params;
    try {
      const attempts = await dao.findAttemptsByStudentAndQuiz(currentUser._id, quizId);
      res.json(attempts);
    } catch (error) {
      res.status(500).json({ error: "Failed to get attempts" });
    }
  };

  const getAttemptById = async (req, res) => {
    
    const currentUser = req.session["currentUser"];
    if (!currentUser) {
      res.sendStatus(401);
      return;
    }

    const { attemptId } = req.params;
    try {
      const attempt = await dao.findAttemptById(attemptId);
      if (!attempt) {
        res.status(404).json({ error: "Attempt not found" });
        return;
      }
      if (attempt.student !== currentUser._id) {
        res.sendStatus(403);
        return;
      }
      res.json(attempt);
    } catch (error) {
      res.status(500).json({ error: "Failed to get attempt" });
    }
  };

  const getAttemptCount = async (req, res) => {
    if (req.session["currentUser"]) {
    }
    
    const currentUser = req.session["currentUser"];
    if (!currentUser) {
      res.sendStatus(401);
      return;
    }

    const { quizId } = req.params;
    try {
      const count = await dao.getCompletedAttemptCount(currentUser._id, quizId);
      res.json({ count });
    } catch (error) {
      res.status(500).json({ error: "Failed to get attempt count" });
    }
  };

  const getLatestAttempt = async (req, res) => {
    
    const currentUser = req.session["currentUser"];
    if (!currentUser) {
      res.sendStatus(401);
      return;
    }

    const { quizId } = req.params;
    try {
      const attempt = await dao.getLatestCompletedAttempt(currentUser._id, quizId);
      res.json(attempt || null);
    } catch (error) {
      res.status(500).json({ error: "Failed to get latest attempt" });
    }
  };

  app.post("/api/quizzes/:quizId/attempts/start", startAttempt);
  app.put("/api/attempts/:attemptId/update", updateAttempt);
  app.post("/api/attempts/:attemptId/submit", submitAttempt);
  app.get("/api/quizzes/:quizId/attempts/in-progress", getInProgressAttempt);
  app.get("/api/quizzes/:quizId/attempts", getStudentAttempts);
  app.get("/api/quizzes/:quizId/attempts/count", getAttemptCount);
  app.get("/api/quizzes/:quizId/attempts/latest", getLatestAttempt);
  app.get("/api/attempts/:attemptId", getAttemptById);
}
