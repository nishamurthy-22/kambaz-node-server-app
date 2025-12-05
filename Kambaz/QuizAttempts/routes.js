import QuizAttemptsDao from "./dao.js";

export default function QuizAttemptsRoutes(app) {
  const dao = QuizAttemptsDao();

  // Start a new quiz attempt (creates draft attempt)
  const startAttempt = async (req, res) => {
    console.log("START ATTEMPT - Session:", req.session);
    console.log("START ATTEMPT - Current User:", req.session["currentUser"]);
    
    const currentUser = req.session["currentUser"];
    if (!currentUser) {
      console.log("START ATTEMPT - No current user, sending 401");
      res.sendStatus(401);
      return;
    }

    const { quizId } = req.params;
    try {
      const attemptCount = await dao.getCompletedAttemptCount(currentUser._id, quizId);
      console.log(`START ATTEMPT - User ${currentUser._id}, Quiz ${quizId}, Completed attempts: ${attemptCount}`);
      
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
      console.log("START ATTEMPT - Created:", attempt._id);
      res.json(attempt);
    } catch (error) {
      console.error("Error starting quiz attempt:", error);
      res.status(500).json({ error: "Failed to start quiz attempt" });
    }
  };

  // Update in-progress attempt
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
      console.error("Error updating quiz attempt:", error);
      res.status(500).json({ error: "Failed to update quiz attempt" });
    }
  };

  // Submit/finalize a quiz attempt
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

      const updates = {
        answers: req.body.answers || attempt.answers,
        score: req.body.score || 0,
        totalPoints: req.body.totalPoints || 0,
        submittedAt: new Date(),
        inProgress: false,
      };
      const submitted = await dao.submitAttempt(attemptId, updates);
      res.json(submitted);
    } catch (error) {
      console.error("Error submitting quiz attempt:", error);
      res.status(500).json({ error: "Failed to submit quiz attempt" });
    }
  };

  // Get in-progress attempt
  const getInProgressAttempt = async (req, res) => {
    console.log("GET IN-PROGRESS - Session:", req.session);
    console.log("GET IN-PROGRESS - Current User:", req.session["currentUser"]);
    
    const currentUser = req.session["currentUser"];
    if (!currentUser) {
      console.log("GET IN-PROGRESS - No current user, sending 401");
      res.sendStatus(401);
      return;
    }

    const { quizId } = req.params;
    try {
      const attempt = await dao.findInProgressAttempt(currentUser._id, quizId);
      console.log("GET IN-PROGRESS - Found:", attempt);
      res.json(attempt || null);
    } catch (error) {
      console.error("Error getting in-progress attempt:", error);
      res.status(500).json({ error: "Failed to get in-progress attempt" });
    }
  };

  // Get all attempts
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
      console.error("Error getting student attempts:", error);
      res.status(500).json({ error: "Failed to get attempts" });
    }
  };

  // Get specific attempt
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
      console.error("Error getting attempt:", error);
      res.status(500).json({ error: "Failed to get attempt" });
    }
  };

  // Get completed attempt count
  const getAttemptCount = async (req, res) => {
    console.log("GET ATTEMPT COUNT - Session:", req.session);
    console.log("GET ATTEMPT COUNT - Current User:", req.session["currentUser"]);
    
    const currentUser = req.session["currentUser"];
    if (!currentUser) {
      console.log("GET ATTEMPT COUNT - No current user, sending 401");
      res.sendStatus(401);
      return;
    }

    const { quizId } = req.params;
    try {
      const count = await dao.getCompletedAttemptCount(currentUser._id, quizId);
      console.log(`GET ATTEMPT COUNT - User ${currentUser._id}, Quiz ${quizId}, Count: ${count}`);
      res.json({ count });
    } catch (error) {
      console.error("Error getting attempt count:", error);
      res.status(500).json({ error: "Failed to get attempt count" });
    }
  };

  // Get latest completed attempt
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
      console.error("Error getting latest attempt:", error);
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
