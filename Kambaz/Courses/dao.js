import { v4 as uuidv4 } from "uuid";
import model from "./model.js";
import EnrollmentsDao from "../Enrollments/dao.js";

export default function CoursesDao() {
  const enrollmentsDao = EnrollmentsDao();

  async function findAllCourses() {
    const courses = await model.find().lean();
    return courses;
  }

  async function findCoursesForEnrolledUser(userId) {
    const enrollments = await enrollmentsDao.findEnrollmentsForUser(userId);
    const enrolledCourseIds = enrollments.map((e) => e.course.toString());
    const courses = await model.find({ _id: { $in: enrolledCourseIds } }).lean();
    return courses;
  }

  async function createCourse(course) {
    const newCourse = { ...course, _id: uuidv4() };
    const created = await model.create(newCourse);
    return created.toObject();
  }

  async function deleteCourse(courseId) {
    const result = await model.deleteOne({ _id: String(courseId) });
    if (result.deletedCount === 0) {
      throw new Error(`Course with id ${courseId} not found`);
    }
    return result;
  }

  async function updateCourse(courseId, courseUpdates) {
    await model.updateOne({ _id: courseId }, { $set: courseUpdates });
    const updated = await model.findById(courseId).lean();
    return updated;
  }

  return { findAllCourses, findCoursesForEnrolledUser, createCourse, deleteCourse, updateCourse };
}