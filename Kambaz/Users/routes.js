import UsersDao from "./dao.js";
import EnrollmentsDao from "../Enrollments/dao.js";
export default function UserRoutes(app, db) {
 const dao = UsersDao(db);
 const enrollmentsDao = EnrollmentsDao(db);
  
  const createUser = (req, res) => {
    const currentUser = req.session["currentUser"];
    if (!currentUser || currentUser.role !== "FACULTY") {
      res.sendStatus(403);
      return;
    }
    const newUser = dao.createUser(req.body);
    res.json(newUser);
  };
  
  const deleteUser = (req, res) => {
    const currentUser = req.session["currentUser"];
    if (!currentUser || currentUser.role !== "FACULTY") {
      res.sendStatus(403);
      return;
    }
    const { userId } = req.params;
    dao.deleteUser(userId);
    res.sendStatus(200);
  };
  
  const findAllUsers = (req, res) => {
    const users = dao.findAllUsers();
    res.json(users);
  };
  
  const findUserById = (req, res) => {
    const { userId } = req.params;
    const user = dao.findUserById(userId);
    if (user) {
      res.json(user);
    } else {
      res.sendStatus(404);
    }
  };

  const findUsersEnrolledInCourse = (req, res) => {
    const { courseId } = req.params;
    const enrollments = enrollmentsDao.findEnrollmentsForCourse(courseId);
    const enrolledUserIds = enrollments.map((e) => e.user);
    const enrolledUsers = dao.findAllUsers().filter((user) =>
      enrolledUserIds.includes(user._id)
    );
    res.json(enrolledUsers);
  };
  const updateUser = (req, res) => {
    const currentUser = req.session["currentUser"];
    const { userId } = req.params;
    const userUpdates = req.body;
    
    // Only faculty can update other users, or users can update themselves
    if (!currentUser) {
      res.sendStatus(401);
      return;
    }
    if (currentUser.role !== "FACULTY" && currentUser._id !== userId) {
      res.sendStatus(403);
      return;
    }
    
    dao.updateUser(userId, userUpdates);
    const updatedUser = dao.findUserById(userId);
    
    // Update session if updating current user
    if (currentUser._id === userId) {
      req.session["currentUser"] = updatedUser;
    }
    
    res.json(updatedUser);
  };
  const signup = (req, res) => { 
        const user = dao.findUserByUsername(req.body.username);
    if (user) {
      res.status(400).json(
        { message: "Username already in use" });
      return;
    }
    const currentUser = dao.createUser(req.body);
    req.session["currentUser"] = currentUser;
    res.json(currentUser);
  };
  const signin = (req, res) => { 
    const { username, password } = req.body;
    const currentUser = dao.findUserByCredentials(username, password);
    if (currentUser) {
      req.session["currentUser"] = currentUser;
    res.json(currentUser);
    } else {
      res.status(401).json({ message: "Unable to login. Try again later." });
    }
  };
  const signout = (req, res) => {
   req.session["currentUser"] = null;
    res.sendStatus(200);
  };
  const profile = async (req, res) => {
    const currentUser = req.session["currentUser"];
    if (!currentUser) {
      res.sendStatus(401);
      return;
    }
    res.json(currentUser);
  };
  app.post("/api/users", createUser);
  app.get("/api/users", findAllUsers);
  app.get("/api/users/:userId", findUserById);
  app.put("/api/users/:userId", updateUser);
  app.delete("/api/users/:userId", deleteUser);
  app.get("/api/courses/:courseId/users", findUsersEnrolledInCourse);
  app.post("/api/users/signup", signup);
  app.post("/api/users/signin", signin);
  app.post("/api/users/signout", signout);
  app.post("/api/users/profile", profile);
}
