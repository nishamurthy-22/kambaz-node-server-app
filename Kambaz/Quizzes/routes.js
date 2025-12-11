import QuizzesDao from "./dao.js";

export default function QuizzesRoutes(app) {
  const dao = QuizzesDao();

  const stripCorrectAnswers = (quiz, userRole) => {
    if (userRole === "FACULTY") {
      return quiz;
    }

    const sanitizedQuiz = { ...quiz };
    if (sanitizedQuiz.questions) {
      sanitizedQuiz.questions = sanitizedQuiz.questions.map(q => {
        const sanitizedQuestion = { ...q };
        
        if (q.type === "MULTIPLE_CHOICE") {
          delete sanitizedQuestion.correctAnswer;
        } else if (q.type === "TRUE_FALSE") {
          delete sanitizedQuestion.correctAnswer;
        } else if (q.type === "FILL_BLANK") {
          if (sanitizedQuestion.blanks) {
            sanitizedQuestion.blanks = sanitizedQuestion.blanks.map(blank => ({
              points: blank.points,
              caseSensitive: blank.caseSensitive
            }));
          }
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
    
    try {
      const quizzes = await dao.findQuizzesForCourse(courseId);
      
      const sanitizedQuizzes = quizzes.map(quiz => 
        stripCorrectAnswers(quiz, currentUser?.role)
      );
      
      res.json(sanitizedQuizzes);
    } catch (error) {
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
      res.status(500).json({ error: "Failed to delete quiz" });
    }
  };
  app.delete("/api/quizzes/:quizId", deleteQuiz);

  const updateQuiz = async (req, res) => {
    const { quizId } = req.params;
    const quizUpdates = req.body;
    
    try {
      const quiz = await dao.updateQuiz(quizId, quizUpdates);
      
      res.json(quiz);
    } catch (error) {
      res.status(500).json({ error: "Failed to update quiz" });
    }
  };
  app.put("/api/quizzes/:quizId", updateQuiz);

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
      
      res.json(quiz);
    } catch (error) {
      res.status(500).json({ error: "Failed to debug quiz" });
    }
  };
  app.get("/api/quizzes/:quizId/debug", debugQuiz);
}
