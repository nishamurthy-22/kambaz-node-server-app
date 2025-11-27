import mongoose from "mongoose";
import enrollmentSchema from "./schema.js";

const enrollmentModel = mongoose.model("Enrollment", enrollmentSchema);
export default enrollmentModel;
