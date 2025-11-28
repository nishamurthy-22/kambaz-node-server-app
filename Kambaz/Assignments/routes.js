import AssignmentsDao from "./dao.js";

export default function AssignmentsRoutes(app) {
  const dao = AssignmentsDao();

  const findAssignmentsForCourse = async (req, res) => {
    const { courseId } = req.params;
    try {
      const assignments = await dao.findAssignmentsForCourse(courseId);
      res.json(assignments);
    } catch (error) {
      console.error("Error finding assignments for course:", error);
      res.status(500).json({ error: "Failed to find assignments for course" });
    }
  };
  app.get("/api/courses/:courseId/assignments", findAssignmentsForCourse);

  const createAssignmentForCourse = async (req, res) => {
    const { courseId } = req.params;
    try {
      const assignment = {
        ...req.body,
        course: courseId,
      };
      const newAssignment = await dao.createAssignment(assignment);
      res.json(newAssignment);
    } catch (error) {
      console.error("Error creating assignment:", error);
      res.status(500).json({ error: "Failed to create assignment" });
    }
  };
  app.post("/api/courses/:courseId/assignments", createAssignmentForCourse);

  const deleteAssignment = async (req, res) => {
    const { assignmentId } = req.params;
    try {
      const result = await dao.deleteAssignment(assignmentId);
      res.json(result);
    } catch (error) {
      console.error("Error deleting assignment:", error);
      res.status(500).json({ error: "Failed to delete assignment" });
    }
  };
  app.delete("/api/assignments/:assignmentId", deleteAssignment);

  const updateAssignment = async (req, res) => {
    const { assignmentId } = req.params;
    const assignmentUpdates = req.body;
    try {
      const assignment = await dao.updateAssignment(assignmentId, assignmentUpdates);
      res.json(assignment);
    } catch (error) {
      console.error("Error updating assignment:", error);
      res.status(500).json({ error: "Failed to update assignment" });
    }
  };
  app.put("/api/assignments/:assignmentId", updateAssignment);
}
