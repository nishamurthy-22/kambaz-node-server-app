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
import QuizzesRoutes from './Kambaz/Quizzes/routes.js';
import QuizAttemptsRoutes from './Kambaz/QuizAttempts/routes.js';
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
  
  const userCount = await UserModel.countDocuments();
  if (userCount === 0) {
    await UserModel.insertMany(usersData);
  }
  
  const courseCount = await CourseModel.countDocuments();
  if (courseCount === 0) {
    await CourseModel.insertMany(coursesData);
  }
  
  const assignmentCount = await AssignmentModel.countDocuments();
  if (assignmentCount === 0) {
    await AssignmentModel.insertMany(assignmentsData);
  }
  
  const enrollmentCount = await EnrollmentModel.countDocuments();
  if (enrollmentCount === 0) {
    try {
      await EnrollmentModel.insertMany(enrollmentsData, { ordered: false });
      const newCount = await EnrollmentModel.countDocuments();
    } catch (error) {
      const newCount = await EnrollmentModel.countDocuments();
    }
  } else {
    try {
      const existingIds = await EnrollmentModel.find().select('_id').lean();
      const existingIdSet = new Set(existingIds.map(e => e._id));
      const missingEnrollments = enrollmentsData.filter(e => !existingIdSet.has(e._id));
      
      if (missingEnrollments.length > 0) {
        await EnrollmentModel.insertMany(missingEnrollments, { ordered: false });
        const finalCount = await EnrollmentModel.countDocuments();
      } else {
      }
    } catch (error) {
    }
  }
}).catch((error) => {
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
      if (origin.includes("vercel.app") || origin.includes("vercel-dns.com")) {
        return callback(null, true);
      }
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

const seedDatabase = async (req, res) => {
  try {
    let results = { users: 0, courses: 0, assignments: 0, enrollments: 0, errors: [] };
    
    const userCount = await UserModel.countDocuments();
    if (userCount === 0) {
      try {
        await UserModel.insertMany(usersData);
        results.users = usersData.length;
      } catch (error) {
        results.errors.push(`Users: ${error.message}`);
      }
    } else {
      results.users = userCount;
    }
    
    const courseCount = await CourseModel.countDocuments();
    if (courseCount === 0) {
      try {
        await CourseModel.insertMany(coursesData);
        results.courses = coursesData.length;
      } catch (error) {
        results.errors.push(`Courses: ${error.message}`);
      }
    } else {
      results.courses = courseCount;
    }
    
    const assignmentCount = await AssignmentModel.countDocuments();
    if (assignmentCount === 0) {
      try {
        await AssignmentModel.insertMany(assignmentsData);
        results.assignments = assignmentsData.length;
      } catch (error) {
        results.errors.push(`Assignments: ${error.message}`);
      }
    } else {
      results.assignments = assignmentCount;
    }
    
    const enrollmentCount = await EnrollmentModel.countDocuments();
    if (enrollmentCount === 0) {
      try {
        await EnrollmentModel.insertMany(enrollmentsData, { ordered: false });
        const newCount = await EnrollmentModel.countDocuments();
        results.enrollments = newCount;
      } catch (error) {
        const newCount = await EnrollmentModel.countDocuments();
        results.enrollments = newCount;
        results.errors.push(`Enrollments: ${error.message}`);
      }
    } else {
      try {
        const existingIds = await EnrollmentModel.find().select('_id').lean();
        const existingIdSet = new Set(existingIds.map(e => e._id));
        const missingEnrollments = enrollmentsData.filter(e => !existingIdSet.has(e._id));
        
        if (missingEnrollments.length > 0) {
          await EnrollmentModel.insertMany(missingEnrollments, { ordered: false });
        }
        const finalCount = await EnrollmentModel.countDocuments();
        results.enrollments = finalCount;
      } catch (error) {
        const finalCount = await EnrollmentModel.countDocuments();
        results.enrollments = finalCount;
        results.errors.push(`Enrollments: ${error.message}`);
      }
    }
    
    res.json({ 
      success: true, 
      message: "Seeding completed",
      results 
    });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
};

app.get("/api/seed", seedDatabase);
app.post("/api/seed", seedDatabase);

const reseedDatabase = async (req, res) => {
  try {
    
    await UserModel.deleteMany({});
    await CourseModel.deleteMany({});
    await AssignmentModel.deleteMany({});
    await EnrollmentModel.deleteMany({});
    
    

    await UserModel.insertMany(usersData);
    await CourseModel.insertMany(coursesData);
    await AssignmentModel.insertMany(assignmentsData);
    await EnrollmentModel.insertMany(enrollmentsData);
    
    const results = {
      users: await UserModel.countDocuments(),
      courses: await CourseModel.countDocuments(),
      assignments: await AssignmentModel.countDocuments(),
      enrollments: await EnrollmentModel.countDocuments()
    };
    
    
    res.json({ 
      success: true, 
      message: "Reseed completed - all data cleared and reseeded",
      results 
    });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
};

app.get("/api/reseed", reseedDatabase);
app.post("/api/reseed", reseedDatabase);

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
QuizzesRoutes(app);
QuizAttemptsRoutes(app);
app.listen(process.env.PORT || 4000)
