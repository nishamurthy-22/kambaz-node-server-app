import QuizzesDao from "./dao.js";

export default function QuizzesRoutes(app) {
  const dao = QuizzesDao();

  const findQuizzesForCourse = async (req, res) => {
    const { courseId } = req.params;
    try {
      const quizzes = await dao.findQuizzesForCourse(courseId);
      res.json(quizzes);
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
    try {
      const quiz = await dao.updateQuiz(quizId, quizUpdates);
      res.json(quiz);
    } catch (error) {
      console.error("Error updating quiz:", error);
      res.status(500).json({ error: "Failed to update quiz" });
    }
  };
  app.put("/api/quizzes/:quizId", updateQuiz);
}

