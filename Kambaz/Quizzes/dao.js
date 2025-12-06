import { v4 as uuidv4 } from "uuid";
import model from "./model.js";

export default function QuizzesDao() {
  async function findQuizzesForCourse(courseId) {
    const quizzes = await model.find({ course: String(courseId) }).lean();
    return quizzes;
  }

  async function findQuizById(quizId) {
    const quiz = await model.findById(String(quizId)).lean();
    return quiz;
  }

  async function createQuiz(quiz) {
    const newQuiz = {
      ...quiz,
      _id: quiz._id || uuidv4(),
    };
    const createdQuiz = await model.create(newQuiz);
    return createdQuiz.toObject();
  }

  async function deleteQuiz(quizId) {
    const result = await model.deleteOne({ _id: String(quizId) });
    if (result.deletedCount === 0) {
      console.warn(`No quiz found to delete with id ${quizId}`);
    }
    return result;
  }

  async function updateQuiz(quizId, quizUpdates) {
    const quiz = await model.findOneAndUpdate(
      { _id: String(quizId) },
      { $set: quizUpdates },
      { new: true }
    ).lean();
    
    if (!quiz) {
      throw new Error(`Quiz with id ${quizId} not found`);
    }
    
    return quiz;
  }

  async function deleteQuizzesForCourse(courseId) {
    const result = await model.deleteMany({ course: String(courseId) });
    return result;
  }

  return {
    findQuizzesForCourse,
    findQuizById,
    createQuiz,
    deleteQuiz,
    updateQuiz,
    deleteQuizzesForCourse,
  };
}
