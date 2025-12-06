# Quick Start Guide

Get up and running with the Kambaz test suite in 5 minutes!

## Prerequisites

- Python 3.8+ installed
- Backend server code ready to run

## Step 1: Start the Backend Server

Open a terminal and start your backend server:

```bash
cd kambaz-node-server-app
npm install  # If not already installed
npm start
```

Wait for the server to start on `http://localhost:4000`

## Step 2: Install Test Dependencies

Open a **new terminal** and navigate to the tests directory:

```bash
cd kambaz-node-server-app/tests
```

Create a virtual environment (optional but recommended):

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Step 3: Run Tests

### Run all tests:

```bash
python main.py
```

### Run with HTML report:

```bash
python main.py --html
```

Then open `test_report.html` in your browser to see the results!

### Run specific test categories:

```bash
# Authentication tests
python main.py --module auth

# User management tests
python main.py --module users

# Quiz tests
python main.py --module quizzes

# Complete student workflow
python main.py --module student_workflow

# All integration tests
python main.py --integration

# All E2E tests
python main.py --e2e
```

## What Gets Tested

- ✅ User signup, login, logout
- ✅ User CRUD operations
- ✅ Course creation and management
- ✅ Student enrollment
- ✅ Modules and assignments
- ✅ Quiz creation (all question types)
- ✅ Quiz submission and grading
- ✅ Complete user workflows
- ✅ Role-based access control

## Viewing Results

After running tests:

1. **Terminal Output**: See pass/fail status in real-time
2. **HTML Report**: Open `test_report.html` for detailed results
3. **JSON Report**: Check `test_report.json` for structured data

## Common Commands

```bash
# List all available test modules
python main.py --list-modules

# Run tests in parallel (faster)
python main.py --parallel

# Verbose output
python main.py --verbose

# Generate both HTML and JSON reports
python main.py --html --json
```

## Troubleshooting

**Backend not running?**
- Make sure you started the server with `npm start`
- Check it's running on `http://localhost:4000`

**Import errors?**
- Make sure you installed dependencies: `pip install -r requirements.txt`
- Activate your virtual environment if you created one

**Tests failing?**
- Check backend server logs for errors
- Ensure MongoDB is running
- Try clearing the database: `python main.py --module seed`

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore test files in `integration/` and `e2e/` directories
- Modify `test_config.py` to customize settings
- Write your own tests using the provided fixtures

Happy Testing! 🎉
