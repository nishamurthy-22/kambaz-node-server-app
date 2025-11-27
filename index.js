import express from 'express';
import mongoose from "mongoose";
import Hello from "./Hello.js";
import Lab5 from "./Lab5/index.js";
import cors from "cors";
import db from "./Kambaz/Database/index.js";
import UserRoutes from "./Kambaz/Users/routes.js";
import CourseRoutes from "./Kambaz/Courses/routes.js";
import ModulesRoutes from './Kambaz/Modules/routes.js';
import AssignmentsRoutes from './Kambaz/Assignments/routes.js';
import EnrollmentsRoutes from './Kambaz/Enrollments/routes.js';
import "dotenv/config";
import session from "express-session";
const CONNECTION_STRING = process.env.DATABASE_CONNECTION_STRING || "mongodb://127.0.0.1:27017/kambaz"
mongoose.connect(CONNECTION_STRING);
const app = express()
const allowedOrigins = [
  "http://localhost:3000",
  "https://kambaz-next-js-git-a5-nisha-murthy-dineshs-projects.vercel.app",
  "https://kambaz-next-js-git-a6-nisha-murthy-dineshs-projects.vercel.app"
]

const corsOptions = {
  credentials: true,
  origin: function (origin, callback) {
    try {
      if (!origin) {
        return callback(null, true);
      }
      
      if (origin.startsWith("http://localhost")) {
        return callback(null, true);
      }
      
      if (allowedOrigins.includes(origin)) {
        return callback(null, true);
      }
      
      if (origin.includes("vercel.app") || origin.includes("vercel-dns.com")) {
        return callback(null, true);
      }
      
      console.log('CORS: Rejected origin:', origin);
      return callback(null, false);
    } catch (error) {
      console.error('CORS origin check error:', error);
      return callback(error, false);
    }
  },
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
  exposedHeaders: ['Content-Type'],
  preflightContinue: false,
  optionsSuccessStatus: 200
};

app.use(cors(corsOptions));

app.options('*', cors(corsOptions));

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
  };
}
app.use(session(sessionOptions));
app.use(express.json());
Lab5(app)
Hello(app)
UserRoutes(app, db);
CourseRoutes(app, db);
ModulesRoutes(app,db);
AssignmentsRoutes(app,db);
EnrollmentsRoutes(app, db);
app.use((err, req, res, next) => {
  console.error('Server Error:', err);
  if (err.message && err.message.includes('CORS')) {
    return res.status(403).json({ error: 'CORS policy violation' });
  }
  res.status(err.status || 500).json({ 
    error: err.message || 'Internal server error' 
  });
});

app.listen(process.env.PORT || 4000, () => {
  console.log(`Server running on port ${process.env.PORT || 4000}`);
})