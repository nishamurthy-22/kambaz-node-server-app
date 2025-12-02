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
import assignmentsData from "./Kambaz/Database/assignments.js";
import enrollmentsData from "./Kambaz/Database/enrollments.js";
import UserModel from "./Kambaz/Users/model.js";
import CourseModel from "./Kambaz/Courses/model.js";
import AssignmentModel from "./Kambaz/Assignments/model.js";
import EnrollmentModel from "./Kambaz/Enrollments/model.js";

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
  
  // Seed assignments if collection is empty
  const assignmentCount = await AssignmentModel.countDocuments();
  if (assignmentCount === 0) {
    console.log("Seeding assignments...");
    await AssignmentModel.insertMany(assignmentsData);
    console.log(`Seeded ${assignmentsData.length} assignments`);
  }
  
  // Seed enrollments if collection is empty
  const enrollmentCount = await EnrollmentModel.countDocuments();
  if (enrollmentCount === 0) {
    console.log("Seeding enrollments...");
    await EnrollmentModel.insertMany(enrollmentsData);
    console.log(`Seeded ${enrollmentsData.length} enrollments`);
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

// Manual seeding endpoint (supports both GET and POST)
const seedDatabase = async (req, res) => {
  try {
    let results = { users: 0, courses: 0, assignments: 0, enrollments: 0, errors: [] };
    
    // Seed users
    const userCount = await UserModel.countDocuments();
    if (userCount === 0) {
      try {
        await UserModel.insertMany(usersData);
        results.users = usersData.length;
        console.log(`Seeded ${usersData.length} users`);
      } catch (error) {
        results.errors.push(`Users: ${error.message}`);
        console.error("Error seeding users:", error);
      }
    } else {
      results.users = userCount;
      console.log(`Users already exist: ${userCount}`);
    }
    
    // Seed courses
    const courseCount = await CourseModel.countDocuments();
    if (courseCount === 0) {
      try {
        await CourseModel.insertMany(coursesData);
        results.courses = coursesData.length;
        console.log(`Seeded ${coursesData.length} courses`);
      } catch (error) {
        results.errors.push(`Courses: ${error.message}`);
        console.error("Error seeding courses:", error);
      }
    } else {
      results.courses = courseCount;
      console.log(`Courses already exist: ${courseCount}`);
    }
    
    // Seed assignments
    const assignmentCount = await AssignmentModel.countDocuments();
    if (assignmentCount === 0) {
      try {
        await AssignmentModel.insertMany(assignmentsData);
        results.assignments = assignmentsData.length;
        console.log(`Seeded ${assignmentsData.length} assignments`);
      } catch (error) {
        results.errors.push(`Assignments: ${error.message}`);
        console.error("Error seeding assignments:", error);
      }
    } else {
      results.assignments = assignmentCount;
      console.log(`Assignments already exist: ${assignmentCount}`);
    }
    
    // Seed enrollments
    const enrollmentCount = await EnrollmentModel.countDocuments();
    if (enrollmentCount === 0) {
      try {
        await EnrollmentModel.insertMany(enrollmentsData);
        results.enrollments = enrollmentsData.length;
        console.log(`Seeded ${enrollmentsData.length} enrollments`);
      } catch (error) {
        results.errors.push(`Enrollments: ${error.message}`);
        console.error("Error seeding enrollments:", error);
      }
    } else {
      results.enrollments = enrollmentCount;
      console.log(`Enrollments already exist: ${enrollmentCount}`);
    }
    
    res.json({ 
      success: true, 
      message: "Seeding completed",
      results 
    });
  } catch (error) {
    console.error("Seeding error:", error);
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
};

// Seed endpoint - must be before other routes
app.get("/api/seed", seedDatabase);
app.post("/api/seed", seedDatabase);

// Test endpoint to verify server is running
app.get("/api/test", (req, res) => {
  res.json({ message: "Server is running", timestamp: new Date().toISOString() });
});

Lab5(app)
Hello(app)
UserRoutes(app);
CourseRoutes(app);
ModulesRoutes(app);
AssignmentsRoutes(app);
EnrollmentsRoutes(app);
app.listen(process.env.PORT || 4000)