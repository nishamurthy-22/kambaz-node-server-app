import model from "./model.js";
import { v4 as uuidv4 } from "uuid";

export default function QuizAttemptsDao() {
  const createAttempt = (attempt) => {
    const attemptWithId = { ...attempt, _id: uuidv4() };
    return model.create(attemptWithId);
  };

  const findAttemptsByStudentAndQuiz = (studentId, quizId) => {
    return model.find({ student: studentId, quiz: quizId }).sort({ attemptNumber: -1 });
  };

  const findAttemptById = (attemptId) => {
    return model.findById(attemptId);
  };

  const getAttemptCount = (studentId, quizId) => {
    return model.countDocuments({ student: studentId, quiz: quizId });
  };

  // Get count of only completed attempts
  const getCompletedAttemptCount = (studentId, quizId) => {
    return model.countDocuments({ 
      student: studentId, 
      quiz: quizId, 
      inProgress: false 
    });
  };

  const getLatestAttempt = (studentId, quizId) => {
    return model.findOne({ student: studentId, quiz: quizId }).sort({ attemptNumber: -1 });
  };

  // Get latest completed attempt
  const getLatestCompletedAttempt = (studentId, quizId) => {
    return model.findOne({ 
      student: studentId, 
      quiz: quizId, 
      inProgress: false 
    }).sort({ attemptNumber: -1 });
  };

  // Find in-progress attempt
  const findInProgressAttempt = (studentId, quizId) => {
    return model.findOne({ 
      student: studentId, 
      quiz: quizId, 
      inProgress: true 
    });
  };

  // Update answers for in-progress attempt
  const updateAttemptAnswers = (attemptId, updates) => {
    return model.findByIdAndUpdate(
      attemptId,
      { $set: updates },
      { new: true }
    );
  };

  // Submit/finalize attempt
  const submitAttempt = (attemptId, updates) => {
    return model.findByIdAndUpdate(
      attemptId,
      { $set: { ...updates, inProgress: false } },
      { new: true }
    );
  };

  return {
    createAttempt,
    findAttemptsByStudentAndQuiz,
    findAttemptById,
    getAttemptCount,
    getCompletedAttemptCount,
    getLatestAttempt,
    getLatestCompletedAttempt,
    findInProgressAttempt,
    updateAttemptAnswers,
    submitAttempt,
  };
}
