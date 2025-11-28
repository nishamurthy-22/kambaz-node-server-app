import { v4 as uuidv4 } from "uuid";
import model from "../Courses/model.js";
export default function ModulesDao() {
async function createModule(courseId, module) {
   const newModule = { ...module, _id: uuidv4() };
   const status = await model.updateOne(
     { _id: courseId },
     { $push: { modules: newModule } }
   );
return newModule;
}

 async function findModulesForCourse(courseId) {
   const course = await model.findById(courseId);
   return course?.modules || [];
 }
 async function deleteModule(courseId, moduleId) {
   const status = await model.updateOne(
     { _id: courseId },
     { $pull: { modules: { _id: moduleId } } }
   );
   if (status.matchedCount === 0) {
     throw new Error(`Course with id ${courseId} not found`);
   }
   return status;
}
async function updateModule(courseId, moduleId, moduleUpdates) {
   const course = await model.findById(courseId);
   if (!course) {
     throw new Error(`Course with id ${courseId} not found`);
   }
   const module = course.modules.id(moduleId);
   if (!module) {
     throw new Error(`Module with id ${moduleId} not found`);
   }
   Object.assign(module, moduleUpdates);
   await course.save();
   return module;
}

 return {
   findModulesForCourse,createModule, deleteModule, updateModule
 };
}
