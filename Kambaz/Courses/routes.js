import CoursesDao from "./dao.js";
import EnrollmentsDao from "../Enrollments/dao.js";
import AssignmentsDao from "../Assignments/dao.js";
export default function CourseRoutes(app) {
  const dao = CoursesDao();
  const enrollmentsDao = EnrollmentsDao();
  const assignmentsDao = AssignmentsDao();
  const createCourse = async (req, res) => {
    const currentUser = req.session["currentUser"];
    if (!currentUser) {
      res.sendStatus(401);
      return;
    }
    // Set the author to the current user
    const courseData = { ...req.body, author: currentUser._id };
    const newCourse = await dao.createCourse(courseData);
    // Auto-enroll faculty in courses they create
    if (currentUser.role === "FACULTY") {
      await enrollmentsDao.enrollUserInCourse(currentUser._id, newCourse._id);
    }
    res.json(newCourse);
  };
  app.post("/api/users/current/courses", createCourse);
  const findAllCourses = async(req, res) => {
    try {
      const courses = await dao.findAllCourses();
      res.json(courses);
    } catch (error) {
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
    const currentUser = req.session["currentUser"];
    if (!currentUser) {
      res.sendStatus(401);
      return;
    }
    // Only faculty can delete courses
    if (currentUser.role !== "FACULTY") {
      res.status(403).json({ error: "Only faculty can delete courses" });
      return;
    }
    try {
      // Check if course exists
      const course = await dao.findCourseById(courseId);
      if (!course) {
        res.status(404).json({ error: "Course not found" });
        return;
      }
      await enrollmentsDao.unenrollAllFromCourse(courseId);
      await assignmentsDao.deleteAssignmentsForCourse(courseId);
      const result = await dao.deleteCourse(courseId);
      res.json(result);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      res.status(500).json({ error: "Failed to delete course: " + errorMessage });
    }
  };
  app.delete("/api/courses/:courseId", deleteCourse);

const updateCourse = async (req, res) => {
    const { courseId } = req.params;
    const courseUpdates = req.body;
    const currentUser = req.session["currentUser"];
    if (!currentUser) {
      res.sendStatus(401);
      return;
    }
    // Only faculty can update courses
    if (currentUser.role !== "FACULTY") {
      res.status(403).json({ error: "Only faculty can edit courses" });
      return;
    }
    // Check if course exists
    const course = await dao.findCourseById(courseId);
    if (!course) {
      res.status(404).json({ error: "Course not found" });
      return;
    }
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
      res.status(500).json({ error: "Failed to find users for course" });
    }
  };
  app.get("/api/courses/:cid/users", findUsersForCourse);

  const findMyCourses = async (req, res) => {
    const currentUser = req.session["currentUser"];
    if (!currentUser) {
      res.sendStatus(401);
      return;
    }
    try {
      let courses;
      if (currentUser.role === "FACULTY") {
        // Faculty see courses they created
        courses = await dao.findCoursesByAuthor(currentUser._id);
      } else {
        // Students see courses they're enrolled in
        courses = await enrollmentsDao.findCoursesForUser(currentUser._id);
      }
      res.json(courses);
    } catch (error) {
      res.status(500).json({ error: "Failed to find courses for user" });
    }
  };
  app.get("/api/users/current/courses", findMyCourses);
}
