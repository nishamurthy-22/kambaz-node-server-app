import EnrollmentsDao from "../Enrollments/dao.js";

export default function EnrollmentsRoutes(app) {
  const dao = EnrollmentsDao();

  const enrollUserInCourse = async (req, res) => {
    const currentUser = req.session["currentUser"];
    if (!currentUser) {
      res.sendStatus(401);
      return;
    }
    const { courseId } = req.params;
    const enrollment = await dao.enrollUserInCourse(currentUser._id, courseId);
    res.json(enrollment);
  };

  const unenrollUserFromCourse = async (req, res) => {
    const currentUser = req.session["currentUser"];
    if (!currentUser) {
      res.sendStatus(401);
      return;
    }
    const { courseId } = req.params;
    await dao.unenrollUserFromCourse(currentUser._id, courseId);
    res.sendStatus(200);
  };

  const findEnrollmentsForUser = async (req, res) => {
    const currentUser = req.session["currentUser"];
    if (!currentUser) {
      res.sendStatus(401);
      return;
    }
    const enrollments = await dao.findEnrollmentsForUser(currentUser._id);
    res.json(enrollments);
  };

  app.post("/api/users/current/courses/:courseId/enrollments", enrollUserInCourse);
  app.delete("/api/users/current/courses/:courseId/enrollments", unenrollUserFromCourse);
  app.get("/api/users/current/enrollments", findEnrollmentsForUser);
}

