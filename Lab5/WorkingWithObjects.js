const assignment = {
  id: 1, title: "NodeJS Assignment",
  description: "Create a NodeJS server with ExpressJS",
  due: "2021-10-10", completed: false, score: 0,
};
const module = {
  id: 1, name: "Module 1",
  description: "Create a module for NodeJS server with ExpressJS",
  course: "Web Dev",
};
export default function WorkingWithObjects(app) {
  const getAssignment = (req, res) => {
    res.json(assignment);
  };
    const getAssignmentTitle = (req, res) => {
    res.json(assignment.title);
  };
  app.get("/lab5/assignment/title", getAssignmentTitle);
  app.get("/lab5/assignment", getAssignment);

   const setAssignmentTitle = (req, res) => {
   const { newTitle } = req.params;
   assignment.title = newTitle;
   res.json(assignment);
 };
 app.get("/lab5/assignment/title/:newTitle", setAssignmentTitle);

 const setAssignmentScore = (req, res) => {
  const { newScore } = req.params;
  assignment.score = Number(newScore);
  res.json(assignment);
};
app.get("/lab5/assignment/score/:newScore", setAssignmentScore);

const setAssignmentCompleted = (req, res) => {
  const { newCompleted } = req.params;
  assignment.completed = newCompleted === "true";
  res.json(assignment);
};
app.get("/lab5/assignment/completed/:newCompleted", setAssignmentCompleted);

 const getModule = (req, res) => {
    res.json(module);
  };
  app.get("/lab5/module", getModule);

const getModuleName = (req, res) => {
    res.json(module.name);
  };
  app.get("/lab5/module/name", getModuleName);

const setModuleName = (req, res) => {
   const { newName} = req.params;
   module.name = newName;
   res.json(module);
 };
 app.get("/lab5/module/name/:newName", setModuleName);

const setModuleDescription = (req, res) => {
  const { newDescription } = req.params;
  module.description = newDescription;
  res.json(module);
};
app.get("/lab5/module/description/:newDescription", setModuleDescription);


};
