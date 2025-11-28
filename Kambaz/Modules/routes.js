import ModulesDao from "../Modules/dao.js";
export default function ModulesRoutes(app) {
  const dao = ModulesDao();
  const findModulesForCourse = async(req, res) => {
    const { courseId } = req.params;
    const modules = await dao.findModulesForCourse(courseId);
    res.json(modules);
  }
    const createModuleForCourse = async (req, res) => {
    const { courseId } = req.params;
    const module = {
      ...req.body,
    };
    const newModule = await dao.createModule(courseId, module);
    res.send(newModule);
  }

  const deleteModule = async (req, res) => {
    const { courseId, moduleId } = req.params;
    try {
      const status = await dao.deleteModule(courseId, moduleId);
      res.json(status);
    } catch (error) {
      console.error("Error deleting module:", error);
      res.status(500).json({ error: "Failed to delete module" });
    }
  }


  const updateModule = async (req, res) => {
    const { courseId, moduleId } = req.params;
    const moduleUpdates = req.body;
    try {
      const module = await dao.updateModule(courseId, moduleId, moduleUpdates);
      res.json(module);
    } catch (error) {
      console.error("Error updating module:", error);
      res.status(500).json({ error: "Failed to update module" });
    }
  }
app.put("/api/courses/:courseId/modules/:moduleId", updateModule);
app.delete("/api/courses/:courseId/modules/:moduleId", deleteModule);
  app.post("/api/courses/:courseId/modules", createModuleForCourse);
  app.get("/api/courses/:courseId/modules", findModulesForCourse);
}
