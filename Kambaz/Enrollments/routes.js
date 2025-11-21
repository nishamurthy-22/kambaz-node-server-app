import EnrollmentsDao from "../Enrollments/dao.js";

export default function EnrollmentsRoutes(app, db) {
  const dao = EnrollmentsDao(db);

  const enrollUserInCourse = (req, res) => {
    const currentUser = req.session["currentUser"];
    if (!currentUser) {
      res.sendStatus(401);
      return;
    }
    const { courseId } = req.params;
    const enrollment = dao.enrollUserInCourse(currentUser._id, courseId);
    res.json(enrollment);
  };

  const unenrollUserFromCourse = (req, res) => {
    const currentUser = req.session["currentUser"];
    if (!currentUser) {
      res.sendStatus(401);
      return;
    }
    const { courseId } = req.params;
    dao.unenrollUserFromCourse(currentUser._id, courseId);
    res.sendStatus(200);
  };

  const findEnrollmentsForUser = (req, res) => {
    const currentUser = req.session["currentUser"];
    if (!currentUser) {
      res.sendStatus(401);
      return;
    }
    const enrollments = dao.findEnrollmentsForUser(currentUser._id);
    res.json(enrollments);
  };

  app.post("/api/users/current/courses/:courseId/enrollments", enrollUserInCourse);
  app.delete("/api/users/current/courses/:courseId/enrollments", unenrollUserFromCourse);
  app.get("/api/users/current/enrollments", findEnrollmentsForUser);
}

