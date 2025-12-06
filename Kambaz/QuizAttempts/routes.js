import QuizAttemptsDao from "./dao.js";
import QuizzesDao from "../Quizzes/dao.js";

export default function QuizAttemptsRoutes(app) {
  const dao = QuizAttemptsDao();
  const quizzesDao = QuizzesDao();

  // Helper function for server-side grading validation
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
        isCorrect = studentAnswer.answer === question.correctChoice;
        pointsEarned = isCorrect ? (question.points || 0) : 0;
      } else if (question.type === "TRUE_FALSE") {
        isCorrect = studentAnswer.answer === question.correctAnswer;
        pointsEarned = isCorrect ? (question.points || 0) : 0;
      } else if (question.type === "FILL_BLANK") {
        // Multi-blank support with partial credit
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
          // Legacy single blank
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
    console.log("===========================================");
    console.log("START ATTEMPT API CALLED");
    console.log("Session exists:", !!req.session);
    console.log("Session ID:", req.session?.id);
    console.log("Current User in session:", req.session["currentUser"] ? "YES" : "NO");
    if (req.session["currentUser"]) {
      console.log("User ID:", req.session["currentUser"]._id);
      console.log("User email:", req.session["currentUser"].email);
    }
    console.log("Quiz ID:", req.params.quizId);
    console.log("===========================================");
    
    const currentUser = req.session["currentUser"];
    if (!currentUser) {
      console.log("❌ NO CURRENT USER - SENDING 401");
      res.sendStatus(401);
      return;
    }

    const { quizId } = req.params;
    try {
      const attemptCount = await dao.getCompletedAttemptCount(currentUser._id, quizId);
      console.log("✓ Attempt count:", attemptCount);
      
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
      console.log("✓ Created attempt:", attempt._id);
      res.json(attempt);
    } catch (error) {
      console.error("❌ Error starting quiz attempt:", error);
      res.status(500).json({ error: "Failed to start quiz attempt" });
    }
  };

  const updateAttempt = async (req, res) => {
    console.log("===========================================");
    console.log("UPDATE ATTEMPT API CALLED");
    console.log("Session exists:", !!req.session);
    console.log("Current User:", req.session["currentUser"] ? "YES" : "NO");
    console.log("Attempt ID:", req.params.attemptId);
    console.log("===========================================");
    
    const currentUser = req.session["currentUser"];
    if (!currentUser) {
      console.log("❌ NO CURRENT USER - SENDING 401");
      res.sendStatus(401);
      return;
    }

    const { attemptId } = req.params;
    try {
      const attempt = await dao.findAttemptById(attemptId);
      if (!attempt) {
        console.log("❌ Attempt not found");
        res.status(404).json({ error: "Attempt not found" });
        return;
      }
      if (attempt.student !== currentUser._id) {
        console.log("❌ Student mismatch - SENDING 403");
        res.sendStatus(403);
        return;
      }
      if (!attempt.inProgress) {
        console.log("❌ Attempt already submitted");
        res.status(400).json({ error: "Cannot update submitted attempt" });
        return;
      }

      const updates = {
        answers: req.body.answers || attempt.answers,
      };
      const updated = await dao.updateAttemptAnswers(attemptId, updates);
      console.log("✓ Updated attempt");
      res.json(updated);
    } catch (error) {
      console.error("❌ Error updating quiz attempt:", error);
      res.status(500).json({ error: "Failed to update quiz attempt" });
    }
  };

  const submitAttempt = async (req, res) => {
    console.log("===========================================");
    console.log("SUBMIT ATTEMPT API CALLED");
    console.log("Session exists:", !!req.session);
    console.log("Current User:", req.session["currentUser"] ? "YES" : "NO");
    console.log("Attempt ID:", req.params.attemptId);
    console.log("===========================================");
    
    const currentUser = req.session["currentUser"];
    if (!currentUser) {
      console.log("❌ NO CURRENT USER - SENDING 401");
      res.sendStatus(401);
      return;
    }

    const { attemptId } = req.params;
    try {
      const attempt = await dao.findAttemptById(attemptId);
      if (!attempt) {
        console.log("❌ Attempt not found");
        res.status(404).json({ error: "Attempt not found" });
        return;
      }
      if (attempt.student !== currentUser._id) {
        console.log("❌ Student mismatch - SENDING 403");
        res.sendStatus(403);
        return;
      }
      if (!attempt.inProgress) {
        console.log("❌ Attempt already submitted");
        res.status(400).json({ error: "Attempt already submitted" });
        return;
      }

      // Get the quiz to validate answers
      const quiz = await quizzesDao.findQuizById(attempt.quiz);
      if (!quiz) {
        console.log("❌ Quiz not found");
        res.status(404).json({ error: "Quiz not found" });
        return;
      }

      // Server-side grading validation
      const { score, answers: gradedAnswers } = gradeQuizAttempt(quiz, req.body.answers || []);
      
      console.log("✓ Server graded score:", score);

      const updates = {
        answers: gradedAnswers,
        score: score, // Use server-calculated score
        totalPoints: quiz.points || 0,
        submittedAt: new Date(),
        inProgress: false,
      };
      const submitted = await dao.submitAttempt(attemptId, updates);
      console.log("✓ Submitted attempt");
      res.json(submitted);
    } catch (error) {
      console.error("❌ Error submitting quiz attempt:", error);
      res.status(500).json({ error: "Failed to submit quiz attempt" });
    }
  };

  const getInProgressAttempt = async (req, res) => {
    console.log("===========================================");
    console.log("GET IN-PROGRESS ATTEMPT API CALLED");
    console.log("Session exists:", !!req.session);
    console.log("Session ID:", req.session?.id);
    console.log("Current User in session:", req.session["currentUser"] ? "YES" : "NO");
    if (req.session["currentUser"]) {
      console.log("User ID:", req.session["currentUser"]._id);
      console.log("User email:", req.session["currentUser"].email);
    }
    console.log("Quiz ID:", req.params.quizId);
    console.log("===========================================");
    
    const currentUser = req.session["currentUser"];
    if (!currentUser) {
      console.log("❌ NO CURRENT USER - SENDING 401");
      res.sendStatus(401);
      return;
    }

    const { quizId } = req.params;
    try {
      const attempt = await dao.findInProgressAttempt(currentUser._id, quizId);
      console.log("✓ In-progress attempt:", attempt ? "FOUND" : "NOT FOUND");
      res.json(attempt || null);
    } catch (error) {
      console.error("❌ Error getting in-progress attempt:", error);
      res.status(500).json({ error: "Failed to get in-progress attempt" });
    }
  };

  const getStudentAttempts = async (req, res) => {
    console.log("===========================================");
    console.log("GET STUDENT ATTEMPTS API CALLED");
    console.log("Session exists:", !!req.session);
    console.log("Current User:", req.session["currentUser"] ? "YES" : "NO");
    console.log("Quiz ID:", req.params.quizId);
    console.log("===========================================");
    
    const currentUser = req.session["currentUser"];
    if (!currentUser) {
      console.log("❌ NO CURRENT USER - SENDING 401");
      res.sendStatus(401);
      return;
    }

    const { quizId } = req.params;
    try {
      const attempts = await dao.findAttemptsByStudentAndQuiz(currentUser._id, quizId);
      console.log("✓ Found attempts:", attempts.length);
      res.json(attempts);
    } catch (error) {
      console.error("❌ Error getting student attempts:", error);
      res.status(500).json({ error: "Failed to get attempts" });
    }
  };

  const getAttemptById = async (req, res) => {
    console.log("===========================================");
    console.log("GET ATTEMPT BY ID API CALLED");
    console.log("Session exists:", !!req.session);
    console.log("Current User:", req.session["currentUser"] ? "YES" : "NO");
    console.log("Attempt ID:", req.params.attemptId);
    console.log("===========================================");
    
    const currentUser = req.session["currentUser"];
    if (!currentUser) {
      console.log("❌ NO CURRENT USER - SENDING 401");
      res.sendStatus(401);
      return;
    }

    const { attemptId } = req.params;
    try {
      const attempt = await dao.findAttemptById(attemptId);
      if (!attempt) {
        console.log("❌ Attempt not found");
        res.status(404).json({ error: "Attempt not found" });
        return;
      }
      if (attempt.student !== currentUser._id) {
        console.log("❌ Student mismatch - SENDING 403");
        res.sendStatus(403);
        return;
      }
      console.log("✓ Found attempt");
      res.json(attempt);
    } catch (error) {
      console.error("❌ Error getting attempt:", error);
      res.status(500).json({ error: "Failed to get attempt" });
    }
  };

  const getAttemptCount = async (req, res) => {
    console.log("===========================================");
    console.log("GET ATTEMPT COUNT API CALLED");
    console.log("Session exists:", !!req.session);
    console.log("Session ID:", req.session?.id);
    console.log("Current User in session:", req.session["currentUser"] ? "YES" : "NO");
    if (req.session["currentUser"]) {
      console.log("User ID:", req.session["currentUser"]._id);
      console.log("User email:", req.session["currentUser"].email);
    }
    console.log("Quiz ID:", req.params.quizId);
    console.log("===========================================");
    
    const currentUser = req.session["currentUser"];
    if (!currentUser) {
      console.log("❌ NO CURRENT USER - SENDING 401");
      res.sendStatus(401);
      return;
    }

    const { quizId } = req.params;
    try {
      const count = await dao.getCompletedAttemptCount(currentUser._id, quizId);
      console.log("✓ Attempt count:", count);
      res.json({ count });
    } catch (error) {
      console.error("❌ Error getting attempt count:", error);
      res.status(500).json({ error: "Failed to get attempt count" });
    }
  };

  const getLatestAttempt = async (req, res) => {
    console.log("===========================================");
    console.log("GET LATEST ATTEMPT API CALLED");
    console.log("Session exists:", !!req.session);
    console.log("Current User:", req.session["currentUser"] ? "YES" : "NO");
    console.log("Quiz ID:", req.params.quizId);
    console.log("===========================================");
    
    const currentUser = req.session["currentUser"];
    if (!currentUser) {
      console.log("❌ NO CURRENT USER - SENDING 401");
      res.sendStatus(401);
      return;
    }

    const { quizId } = req.params;
    try {
      const attempt = await dao.getLatestCompletedAttempt(currentUser._id, quizId);
      console.log("✓ Latest attempt:", attempt ? "FOUND" : "NOT FOUND");
      res.json(attempt || null);
    } catch (error) {
      console.error("❌ Error getting latest attempt:", error);
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
