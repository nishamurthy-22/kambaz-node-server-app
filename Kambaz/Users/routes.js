import UsersDao from "./dao.js";
import EnrollmentsDao from "../Enrollments/dao.js";

export default function UserRoutes(app) {
  const dao = UsersDao();
  const enrollmentsDao = EnrollmentsDao();
  
  const createUser = async (req, res) => {
    const user = await dao.createUser(req.body);
    res.json(user);
  };

  const deleteUser = async (req, res) => {
    const status = await dao.deleteUser(req.params.userId);
    res.json(status);
  };

  const findAllUsers = async (req, res) => {
    const { role, name } = req.query;
    if (role) {
      const users = await dao.findUsersByRole(role);
      res.json(users);
      return;
    }
    if (name) {
      const users = await dao.findUsersByPartialName(name);
      res.json(users);
      return;
    }
    const users = await dao.findAllUsers();
    res.json(users);
  };

  const findUserById = async (req, res) => {
    const { userId } = req.params;
    const user = await dao.findUserById(userId);
    if (user) {
      res.json(user);
    } else {
      res.sendStatus(404);
    }
  };

  const findUsersEnrolledInCourse = async (req, res) => {
    const { courseId } = req.params;
    const enrollments = await enrollmentsDao.findEnrollmentsForCourse(courseId);
    const enrolledUserIds = enrollments.map((e) => e.user.toString());
    const allUsers = await dao.findAllUsers();
    const usersInCourse = allUsers.filter((user) =>
      enrolledUserIds.includes(user._id.toString())
    );
    res.json(usersInCourse);
  };

  const updateUser = async (req, res) => {
    const { userId } = req.params;
    const userUpdates = req.body;
    await dao.updateUser(userId, userUpdates);
    const currentUser = req.session["currentUser"];
    if (currentUser && currentUser._id === userId) {
      req.session["currentUser"] = { ...currentUser, ...userUpdates };
    }
    res.json(currentUser);
  };

  const signup = async (req, res) => {
    try {
      const existingUser = await dao.findUserByUsername(req.body.username);
      if (existingUser) {
        console.log(`SIGNUP - Username '${req.body.username}' already exists`);
        res.status(400).json({ message: "Username already in use" });
        return;
      }
      
      const currentUser = await dao.createUser(req.body);
      req.session["currentUser"] = currentUser;
      console.log(`SIGNUP - Created user: ${currentUser.username} (${currentUser._id})`);
      res.json(currentUser);
    } catch (error) {
      console.error("SIGNUP - Error:", error);
      res.status(500).json({ message: "Signup failed. Please try again." });
    }
  };

  const signin = async (req, res) => {
    try {
      const { username, password } = req.body;
      
      console.log(`SIGNIN - Attempt for username: '${username}'`);
      
      if (!username || !password) {
        console.log("SIGNIN - Missing username or password");
        res.status(400).json({ message: "Username and password are required" });
        return;
      }

      const currentUser = await dao.findUserByCredentials(username, password);
      
      if (currentUser) {
        req.session["currentUser"] = currentUser;
        console.log(`SIGNIN - Success: ${currentUser.username} (${currentUser.role})`);
        res.json(currentUser);
      } else {
        // Check if username exists
        const userExists = await dao.findUserByUsername(username);
        if (userExists) {
          console.log(`SIGNIN - Failed: Username '${username}' exists but wrong password`);
          res.status(401).json({ message: "Invalid password" });
        } else {
          console.log(`SIGNIN - Failed: Username '${username}' not found`);
          res.status(401).json({ message: "Username not found" });
        }
      }
    } catch (error) {
      console.error("SIGNIN - Error:", error);
      res.status(500).json({ message: "Server error. Please try again later." });
    }
  };

  const signout = async (req, res) => {
    const username = req.session["currentUser"]?.username;
    req.session["currentUser"] = null;
    console.log(`SIGNOUT - User: ${username || 'unknown'}`);
    res.sendStatus(200);
  };

  const profile = async (req, res) => {
    const currentUser = req.session["currentUser"];
    if (!currentUser) {
      console.log("PROFILE - No current user in session");
      res.sendStatus(401);
      return;
    }
    console.log(`PROFILE - User: ${currentUser.username}`);
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
