import CoursesDao from "./dao.js";
import EnrollmentsDao from "../Enrollments/dao.js";
import AssignmentsDao from "../Assignments/dao.js";
export default function CourseRoutes(app) {
  const dao = CoursesDao();
  const enrollmentsDao = EnrollmentsDao();
  const assignmentsDao = AssignmentsDao();
  const createCourse = async (req, res) => {
    const currentUser = req.session["currentUser"];
    const newCourse = await dao.createCourse(req.body);
    res.json(newCourse);
  };
  app.post("/api/users/current/courses", createCourse);
  const findAllCourses = async(req, res) => {
    try {
      const courses = await dao.findAllCourses();
      res.json(courses);
    } catch (error) {
      console.error("Error fetching courses:", error);
      res.status(500).json({ error: "Failed to fetch courses" });
    }
  }
  app.get("/api/courses", findAllCourses);

    const findCoursesForEnrolledUser = async(req, res) => {
    let { userId } = req.params;
    if (userId === "current") {
      const currentUser = req.session["currentUser"];
      if (!currentUser) {
        res.sendStatus(401);
        return;
      }
      userId = currentUser._id;
    }
    const courses = await enrollmentsDao.findCoursesForUser(userId);
    res.json(courses);
  };
  app.get("/api/users/:userId/courses", findCoursesForEnrolledUser);

  const deleteCourse = async (req, res) => {
    const { courseId } = req.params;
    try {
      // Delete all enrollments for this course
      await enrollmentsDao.unenrollAllFromCourse(courseId);
      // Delete all assignments for this course
      await assignmentsDao.deleteAssignmentsForCourse(courseId);
      // Delete the course itself
      const result = await dao.deleteCourse(courseId);
      res.json(result);
    } catch (error) {
      console.error("Error deleting course:", error);
      const errorMessage = error instanceof Error ? error.message : String(error);
      res.status(500).json({ error: "Failed to delete course: " + errorMessage });
    }
  };
  app.delete("/api/courses/:courseId", deleteCourse);

const updateCourse = async (req, res) => {
    const { courseId } = req.params;
    const courseUpdates = req.body;
    const status = await dao.updateCourse(courseId, courseUpdates);
    res.send(status);
  }
  app.put("/api/courses/:courseId", updateCourse);

  const enrollUserInCourse = async (req, res) => {
    let { uid, cid } = req.params;
    if (uid === "current") {
      const currentUser = req.session["currentUser"];
      if (!currentUser) {
        res.sendStatus(401);
        return;
      }
      uid = currentUser._id;
    }
    try {
      const enrollment = await enrollmentsDao.enrollUserInCourse(uid, cid);
      res.json(enrollment);
    } catch (error) {
      console.error("Error enrolling user in course:", error);
      res.status(500).json({ error: "Failed to enroll user in course" });
    }
  };
  
  const unenrollUserFromCourse = async (req, res) => {
    let { uid, cid } = req.params;
    if (uid === "current") {
      const currentUser = req.session["currentUser"];
      if (!currentUser) {
        res.sendStatus(401);
        return;
      }
      uid = currentUser._id;
    }
    try {
      await enrollmentsDao.unenrollUserFromCourse(uid, cid);
      res.sendStatus(200);
    } catch (error) {
      console.error("Error unenrolling user from course:", error);
      res.status(500).json({ error: "Failed to unenroll user from course" });
    }
  };
  app.post("/api/users/:uid/courses/:cid", enrollUserInCourse);
  app.delete("/api/users/:uid/courses/:cid", unenrollUserFromCourse);

  const findUsersForCourse = async (req, res) => {
    const { cid } = req.params;
    try {
      const users = await enrollmentsDao.findUsersForCourse(cid);
      res.json(users);
    } catch (error) {
      console.error("Error finding users for course:", error);
      res.status(500).json({ error: "Failed to find users for course" });
    }
  };
  app.get("/api/courses/:cid/users", findUsersForCourse);
}
