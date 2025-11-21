import { v4 as uuidv4 } from "uuid";
export default function EnrollmentsDao(db) {
  function enrollUserInCourse(userId, courseId) {
    const { enrollments } = db;
    const exists = enrollments.some(
      (e) => e.user === userId && e.course === courseId
    );
    if (!exists) {
      enrollments.push({ _id: uuidv4(), user: userId, course: courseId });
    }
    return enrollments.find((e) => e.user === userId && e.course === courseId);
  }

  function unenrollUserFromCourse(userId, courseId) {
    const { enrollments } = db;
    db.enrollments = enrollments.filter(
      (e) => !(e.user === userId && e.course === courseId)
    );
  }

  function findEnrollmentsForUser(userId) {
    const { enrollments } = db;
    return enrollments.filter((e) => e.user === userId);
  }

  function findEnrollmentsForCourse(courseId) {
    const { enrollments } = db;
    return enrollments.filter((e) => e.course === courseId);
  }

  return { enrollUserInCourse, unenrollUserFromCourse, findEnrollmentsForUser, findEnrollmentsForCourse };
}
