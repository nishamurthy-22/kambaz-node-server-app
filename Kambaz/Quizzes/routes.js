import QuizzesDao from "./dao.js";

export default function QuizzesRoutes(app) {
  const dao = QuizzesDao();

  // Helper to remove correct answers from quiz questions
  const stripCorrectAnswers = (quiz, userRole) => {
    console.log("===== STRIP CORRECT ANSWERS =====");
    console.log("User Role:", userRole);
    console.log("=================================");
    
    // Faculty can see everything
    if (userRole === "FACULTY") {
      console.log("✓ Faculty - returning full quiz with correct answers");
      return quiz;
    }

    console.log("❌ Student - stripping correct answers");
    
    // Students don't get correct answers
    const sanitizedQuiz = { ...quiz };
    if (sanitizedQuiz.questions) {
      sanitizedQuiz.questions = sanitizedQuiz.questions.map(q => {
        const sanitizedQuestion = { ...q };
        
        // Remove correct answers based on question type
        if (q.type === "MULTIPLE_CHOICE") {
          delete sanitizedQuestion.correctAnswer;
        } else if (q.type === "TRUE_FALSE") {
          delete sanitizedQuestion.correctAnswer;
        } else if (q.type === "FILL_BLANK") {
          // Remove possibleAnswers from blanks
          if (sanitizedQuestion.blanks) {
            sanitizedQuestion.blanks = sanitizedQuestion.blanks.map(blank => ({
              points: blank.points,
              caseSensitive: blank.caseSensitive
              // possibleAnswers removed
            }));
          }
          // Also remove legacy possibleAnswers
          delete sanitizedQuestion.possibleAnswers;
        }
        
        return sanitizedQuestion;
      });
    }
    
    return sanitizedQuiz;
  };

  const findQuizzesForCourse = async (req, res) => {
    const { courseId } = req.params;
    const currentUser = req.session["currentUser"];
    
    console.log("===== FIND QUIZZES FOR COURSE =====");
    console.log("Current User exists:", !!currentUser);
    console.log("Current User Role:", currentUser?.role);
    console.log("===================================");
    
    try {
      const quizzes = await dao.findQuizzesForCourse(courseId);
      
      // Strip correct answers for students
      const sanitizedQuizzes = quizzes.map(quiz => 
        stripCorrectAnswers(quiz, currentUser?.role)
      );
      
      res.json(sanitizedQuizzes);
    } catch (error) {
      console.error("Error finding quizzes for course:", error);
      res.status(500).json({ error: "Failed to find quizzes for course" });
    }
  };
  app.get("/api/courses/:courseId/quizzes", findQuizzesForCourse);

  const createQuizForCourse = async (req, res) => {
    const { courseId } = req.params;
    try {
      const quiz = {
        ...req.body,
        course: courseId,
      };
      const newQuiz = await dao.createQuiz(quiz);
      res.json(newQuiz);
    } catch (error) {
      console.error("Error creating quiz:", error);
      res.status(500).json({ error: "Failed to create quiz" });
    }
  };
  app.post("/api/courses/:courseId/quizzes", createQuizForCourse);

  const deleteQuiz = async (req, res) => {
    const { quizId } = req.params;
    try {
      const result = await dao.deleteQuiz(quizId);
      res.json(result);
    } catch (error) {
      console.error("Error deleting quiz:", error);
      res.status(500).json({ error: "Failed to delete quiz" });
    }
  };
  app.delete("/api/quizzes/:quizId", deleteQuiz);

  const updateQuiz = async (req, res) => {
    const { quizId } = req.params;
    const quizUpdates = req.body;
    
    console.log("===== UPDATE QUIZ =====");
    console.log("Quiz ID:", quizId);
    console.log("Has questions:", !!quizUpdates.questions);
    console.log("Questions count:", quizUpdates.questions?.length);
    if (quizUpdates.questions && quizUpdates.questions.length > 0) {
      console.log("First question correctAnswer:", quizUpdates.questions[0].correctAnswer);
    }
    console.log("=======================");
    
    try {
      const quiz = await dao.updateQuiz(quizId, quizUpdates);
      
      console.log("===== QUIZ AFTER UPDATE =====");
      console.log("Has questions:", !!quiz.questions);
      if (quiz.questions && quiz.questions.length > 0) {
        console.log("First question correctAnswer:", quiz.questions[0].correctAnswer);
      }
      console.log("=============================");
      
      res.json(quiz);
    } catch (error) {
      console.error("Error updating quiz:", error);
      res.status(500).json({ error: "Failed to update quiz" });
    }
  };
  app.put("/api/quizzes/:quizId", updateQuiz);

  // Debug route to check quiz data (faculty only)
  const debugQuiz = async (req, res) => {
    const { quizId } = req.params;
    const currentUser = req.session["currentUser"];
    
    if (currentUser?.role !== "FACULTY") {
      res.sendStatus(403);
      return;
    }
    
    try {
      const quiz = await dao.findQuizById(quizId);
      if (!quiz) {
        res.status(404).json({ error: "Quiz not found" });
        return;
      }
      
      console.log("=== QUIZ DEBUG ===");
      console.log("Quiz ID:", quiz._id);
      console.log("Title:", quiz.title);
      console.log("Total Points:", quiz.points);
      console.log("Questions:", quiz.questions?.length);
      
      quiz.questions?.forEach((q, index) => {
        console.log(`\nQuestion ${index + 1}:`);
        console.log("  Type:", q.type);
        console.log("  Points:", q.points);
        if (q.type === "FILL_BLANK") {
          console.log("  Blanks:", q.blanks?.length || 0);
          q.blanks?.forEach((blank, bIndex) => {
            console.log(`    Blank ${bIndex + 1}:`, {
              points: blank.points,
              answers: blank.possibleAnswers,
              caseSensitive: blank.caseSensitive
            });
          });
        }
      });
      console.log("=================");
      
      res.json(quiz);
    } catch (error) {
      console.error("Error debugging quiz:", error);
      res.status(500).json({ error: "Failed to debug quiz" });
    }
  };
  app.get("/api/quizzes/:quizId/debug", debugQuiz);
}
