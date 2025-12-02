import express from 'express';
import mongoose from "mongoose";
import Hello from "./Hello.js";
import Lab5 from "./Lab5/index.js";
import cors from "cors";
import UserRoutes from "./Kambaz/Users/routes.js";
import CourseRoutes from "./Kambaz/Courses/routes.js";
import ModulesRoutes from './Kambaz/Modules/routes.js';
import AssignmentsRoutes from './Kambaz/Assignments/routes.js';
import EnrollmentsRoutes from './Kambaz/Enrollments/routes.js';
import "dotenv/config";
import session from "express-session";
import usersData from "./Kambaz/Database/users.js";
import coursesData from "./Kambaz/Database/courses.js";
import UserModel from "./Kambaz/Users/model.js";
import CourseModel from "./Kambaz/Courses/model.js";

const CONNECTION_STRING = process.env.DATABASE_CONNECTION_STRING || "mongodb://127.0.0.1:27017/kambaz";
mongoose.connect(CONNECTION_STRING).then(async () => {
  console.log("Connected to MongoDB");
  
  // Seed users if collection is empty
  const userCount = await UserModel.countDocuments();
  if (userCount === 0) {
    console.log("Seeding users...");
    await UserModel.insertMany(usersData);
    console.log(`Seeded ${usersData.length} users`);
  }
  
  // Seed courses if collection is empty
  const courseCount = await CourseModel.countDocuments();
  if (courseCount === 0) {
    console.log("Seeding courses...");
    await CourseModel.insertMany(coursesData);
    console.log(`Seeded ${coursesData.length} courses`);
  }
}).catch((error) => {
  console.error("MongoDB connection error:", error);
});

const app = express();
const allowedOrigins = [
  "http://localhost:3000",
  "https://kambaz-next-js-git-a5-nisha-murthy-dineshs-projects.vercel.app",
"https://kambaz-next-js-git-a6-nisha-murthy-dineshs-projects.vercel.app"]

app.use(
  cors({
    credentials: true,
    origin: function (origin, callback) {
      if (!origin) return callback(null, true);
      if (allowedOrigins.includes(origin)) {
        return callback(null, true);
      }
      // Allow any Vercel deployment
      if (origin.includes("vercel.app") || origin.includes("vercel-dns.com")) {
        return callback(null, true);
      }
      // Allow localhost
      if (origin.startsWith("http://localhost")) {
        return callback(null, true);
      }
      return callback(null, false);
    },
  })
);
const sessionOptions = {
  secret: process.env.SESSION_SECRET || "kambaz",
  resave: false,
  saveUninitialized: false,
};
if (process.env.SERVER_ENV !== "development") {
  sessionOptions.proxy = true;
  sessionOptions.cookie = {
    sameSite: "none",
    secure: true,
    domain: process.env.SERVER_URL,
  };
}
app.use(session(sessionOptions));
app.use(express.json());
Lab5(app)
Hello(app)
UserRoutes(app);
CourseRoutes(app);
ModulesRoutes(app);
AssignmentsRoutes(app);
EnrollmentsRoutes(app);
app.listen(process.env.PORT || 4000)