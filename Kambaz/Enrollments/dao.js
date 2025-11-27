import model from "./model.js";

export default function EnrollmentsDao() {

  const enrollUserInCourse = async (userId, courseId) => {
    const enrollment = await model.findOneAndUpdate(
      { user: userId, course: courseId },
      { user: userId, course: courseId },
      { upsert: true, new: true }
    ).lean();
    return enrollment;
  };

  const unenrollUserFromCourse = async (userId, courseId) => {
    await model.deleteOne({ user: userId, course: courseId });
  };

  const findEnrollmentsForUser = async (userId) => {
    const enrollments = await model.find({ user: userId }).lean();
    return enrollments;
  };

  const findEnrollmentsForCourse = async (courseId) => {
    const enrollments = await model.find({ course: courseId }).lean();
    return enrollments;
  };

  return {
    enrollUserInCourse,
    unenrollUserFromCourse,
    findEnrollmentsForUser,
    findEnrollmentsForCourse
  };
}
