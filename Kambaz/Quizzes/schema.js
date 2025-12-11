import mongoose from "mongoose";

const questionSchema = new mongoose.Schema({
  _id: String,
  type: { 
    type: String, 
    enum: ["MULTIPLE_CHOICE", "TRUE_FALSE", "FILL_BLANK"],
    required: true 
  },
  title: String,
  points: { type: Number, default: 1 },
  question: String,
  
  choices: [String],
  correctAnswer: String,
  
  blanks: [{
    possibleAnswers: [String],
    points: { type: Number, default: 1 },
    caseSensitive: { type: Boolean, default: false }
  }],
  possibleAnswers: [String],
  caseSensitive: { type: Boolean, default: false }
});

const quizSchema = new mongoose.Schema(
  {
    _id: String,
    title: String,
    course: { type: String, ref: "CourseModel" },
    description: String,
    points: Number,
    "Available Date": String,
    "Available Until Date": String,
    "Due Date": String,
    "Questions": Number,
    published: { type: Boolean, default: false },
    quizType: { type: String, default: "Graded Quiz" },
    assignmentGroup: { type: String, default: "QUIZZES" },
    shuffleAnswers: { type: Boolean, default: true },
    hasTimeLimit: { type: Boolean, default: true },
    timeLimit: { type: Number, default: 20 },
    multipleAttempts: { type: Boolean, default: false },
    attemptsAllowed: { type: Number, default: 1 },
    showCorrectAnswers: String,
    accessCode: { type: String, default: "" },
    oneQuestionAtATime: { type: Boolean, default: true },
    webcamRequired: { type: Boolean, default: false },
    lockQuestionsAfterAnswering: { type: Boolean, default: false },
    questions: [questionSchema]
  },
  { collection: "quizzes" }
);

export default quizSchema;
