import mongoose from "mongoose";

const quizAttemptSchema = new mongoose.Schema(
  {
    _id: String,
    quiz: { type: String, ref: "QuizModel", required: true },
    student: { type: String, ref: "UserModel", required: true },
    attemptNumber: { type: Number, required: true },
    answers: [{
      question: String,
      answer: mongoose.Schema.Types.Mixed, // Can be String, Number, Boolean
      correct: Boolean,
      points: Number
    }],
    score: Number,
    totalPoints: Number,
    submittedAt: Date, // null if in-progress
    startedAt: { type: Date, default: Date.now },
    inProgress: { type: Boolean, default: true }, // true while taking, false after submit
  },
  { collection: "quizattempts" }
);

export default quizAttemptSchema;
