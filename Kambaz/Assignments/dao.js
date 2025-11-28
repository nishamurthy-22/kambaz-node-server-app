import { v4 as uuidv4 } from "uuid";
import model from "./model.js";

export default function AssignmentsDao() {
  async function findAssignmentsForCourse(courseId) {
    const assignments = await model.find({ course: String(courseId) }).lean();
    return assignments;
  }

  async function createAssignment(assignment) {
    const newAssignment = {
      ...assignment,
      _id: assignment._id || uuidv4(),
    };
    const createdAssignment = await model.create(newAssignment);
    return createdAssignment.toObject();
  }

  async function deleteAssignment(assignmentId) {
    const result = await model.deleteOne({ _id: String(assignmentId) });
    if (result.deletedCount === 0) {
      console.warn(`No assignment found to delete with id ${assignmentId}`);
    }
    return result;
  }

  async function updateAssignment(assignmentId, assignmentUpdates) {
    const assignment = await model.findOneAndUpdate(
      { _id: String(assignmentId) },
      { $set: assignmentUpdates },
      { new: true }
    ).lean();
    
    if (!assignment) {
      throw new Error(`Assignment with id ${assignmentId} not found`);
    }
    
    return assignment;
  }

  async function deleteAssignmentsForCourse(courseId) {
    const result = await model.deleteMany({ course: String(courseId) });
    return result;
  }

  return {
    findAssignmentsForCourse,
    createAssignment,
    deleteAssignment,
    updateAssignment,
    deleteAssignmentsForCourse,
  };
}
