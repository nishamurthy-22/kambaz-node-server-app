import mongoose from "mongoose";

const assignmentSchema = new mongoose.Schema(
  {
    _id: String,
    title: String,
    course: { type: String, ref: "CourseModel" },
    description: String,
    points: Number,
    "Not available until": String,
    "Due": String,
    "Available until": String,
  },
  { collection: "assignments" }
);

export default assignmentSchema;

