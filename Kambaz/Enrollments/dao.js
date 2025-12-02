import model from "./model.js";

export default function EnrollmentsDao() {

  const enrollUserInCourse = async (userId, courseId) => {
    const userIdStr = String(userId);
    const courseIdStr = String(courseId);
    const enrollment = await model.findOneAndUpdate(
      { user: userIdStr, course: courseIdStr },
      { user: userIdStr, course: courseIdStr },
      { upsert: true, new: true }
    ).lean();
    return enrollment;
  };

 async function findCoursesForUser(userId) {
   const enrollments = await model.find({ user: userId }).populate("course");
   return enrollments.map((enrollment) => enrollment.course);
 }
 async function findUsersForCourse(courseId) {
   const enrollments = await model.find({ course: String(courseId) }).populate("user");
   return enrollments.map((enrollment) => enrollment.user);
 }
  const unenrollUserFromCourse = async (userId, courseId) => {
    const result = await model.deleteOne({ 
      user: String(userId), 
      course: String(courseId) 
    });
    if (result.deletedCount === 0) {
      console.warn(`No enrollment found to delete for user ${userId} and course ${courseId}`);
    }
    return result;
  };

  const findEnrollmentsForUser = async (userId) => {
    const enrollments = await model.find({ user: String(userId) }).lean();
    return enrollments;
  };

  const findEnrollmentsForCourse = async (courseId) => {
    const enrollments = await model.find({ course: courseId }).lean();
    return enrollments;
  };

  const unenrollAllFromCourse = async (courseId) => {
    await model.deleteMany({ course: String(courseId) });
  };

  return {
    enrollUserInCourse,
    unenrollUserFromCourse,
    findEnrollmentsForUser,
    findEnrollmentsForCourse,
    unenrollAllFromCourse,
    findCoursesForUser,
    findUsersForCourse,
  };
}
