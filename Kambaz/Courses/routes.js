import CoursesDao from "./dao.js";
import EnrollmentsDao from "../Enrollments/dao.js";
export default function CourseRoutes(app, db) {
  const dao = CoursesDao(db);
   const enrollmentsDao = EnrollmentsDao(db);
  const createCourse = (req, res) => {
    const currentUser = req.session["currentUser"];
    const newCourse = dao.createCourse(req.body);
    res.json(newCourse);
  };
  app.post("/api/users/current/courses", createCourse);
  const findAllCourses = (req, res) => {
    const courses = dao.findAllCourses();
    res.send(courses);
  }
  app.get("/api/courses", findAllCourses);

    const findCoursesForEnrolledUser = (req, res) => {
    let { userId } = req.params;
    if (userId === "current") {
      const currentUser = req.session["currentUser"];
      if (!currentUser) {
        res.sendStatus(401);
        return;
      }
      userId = currentUser._id;
    }
    const courses = dao.findCoursesForEnrolledUser(userId);
    res.json(courses);
  };
  app.get("/api/users/:userId/courses", findCoursesForEnrolledUser);

const deleteCourse = (req, res) => {
    const { courseId } = req.params;
    const status = dao.deleteCourse(courseId);
    res.send(status);
  }
  app.delete("/api/courses/:courseId", deleteCourse);

const updateCourse = (req, res) => {
    const { courseId } = req.params;
    const courseUpdates = req.body;
    const status = dao.updateCourse(courseId, courseUpdates);
    res.send(status);
  }
  app.put("/api/courses/:courseId", updateCourse);
}
