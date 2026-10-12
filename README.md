# DB Lab 2 — Login & To-Do Application

A responsive Flask and MySQL web application developed for the Introduction to Database Systems Lab 2. Taskly allows users to register, log in, and manage their personal to-do lists.

## 1. Team Members and Contributions

* **Mohamed Hassan Elragal — 2304246**

  * Database connection and integration.
  * User registration and login.
  * Password hashing and session management.
  * Authentication and validation.

* **Mohamed Ashraf Kamel — 2304059**

  * Task management functionality (add, edit, complete, and delete).
  * Frontend development and styling.
  * Responsive layout and user interface.

* **Both team members**

  * Testing and debugging.
  * Integration of the frontend, backend, and database.
  * Implementation and testing of bonus features.
  * Documentation.

## 2. Technologies Used

### Backend

* Python 3
* Flask
* PyMySQL
* bcrypt
* python-dotenv

### Frontend

* HTML
* CSS
* JavaScript
* Jinja templates

### Database

* MySQL
* Relational tables with primary keys and foreign keys
* Parameterized SQL queries without an ORM

## 3. How to Run the Application

### Requirements

Install the following software on your machine:

* Python 3.10 or newer
* MySQL Server
* MySQL Workbench (optional)
* Git (if cloning the repository)

### Step 1: Get the Project

Clone the repository:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd db-lab2-flask
```

Alternatively, download and extract the project, then open a terminal inside its folder.

### Step 2: Create and Activate a Virtual Environment

On Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### Step 4: Set Up the Database

1. Start the MySQL server.
2. Open MySQL Workbench or the MySQL command line.
3. Open and execute `database/schema.sql`.

**Warning:** Check the SQL file before executing it. If it contains `DROP DATABASE IF EXISTS registration`, it will delete the existing `registration` database and recreate it.

### Step 5: Configure Environment Variables

Copy `.env.example` to `.env`.

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

On macOS or Linux:

```bash
cp .env.example .env
```

Open `.env` and enter your own MySQL username, password, database name, and a strong Flask secret key.

Do not upload `.env` to GitHub because it contains private credentials. Keep `.env.example` with placeholder values.

### Step 6: Start the Server

With the virtual environment activated, run:

```bash
python app.py
```

### Step 7: Open the Application

Open your browser and visit:

http://127.0.0.1:5000

Register an account or log in to start using Taskly.

## 4. Requirements and Features (R1–R10)

The application implements the following core features:

* **R1 — User Registration:** Users can register with their name, email, password, and password confirmation.
* **R2 — Duplicate Email Validation:** Registration is rejected when the email address already exists, displaying `Email Already Exists`.
* **R3 — User Login:** Users can log in with their registered email and password.
* **R4 — Login Error Handling:** Unknown emails and incorrect passwords display the same `Invalid email or password` message.
* **R5 — Session Management:** Logged-in users can access their personal task list and log out.
* **R6 — Add Tasks:** Users can create new to-do items.
* **R7 — Edit Tasks:** Users can update existing task titles.
* **R8 — Complete Tasks:** Users can mark tasks as done or not done.
* **R9 — Delete Tasks:** Users can delete tasks after confirming the action.
* **R10 — Validation and Security:** Required fields are validated, SQL queries are parameterized, and task operations are restricted to the logged-in user's ID.

### Bonus Features

* Optional task due dates.
* Search tasks by title.
* Filter tasks by all, open, or completed status.
* Display total, open, and completed task counts.
* Dark mode and light mode with the selected theme saved in the browser.
* Due-date indicators for overdue tasks and tasks due today.
* Responsive layout for mobile and desktop screens.


## 5. Database and Security Questions

### (a) Why do UPDATE and DELETE contain `AND user_id = ?`, and what changes if it is removed?

The condition ensures that users can only update or delete tasks belonging to their own accounts. The `user_id` comes from the logged-in user's session.

If the condition is removed, a user who guesses another task's ID could potentially modify or delete another user's task. Including the condition helps enforce task ownership.

### (b) What happens if you insert a to-do for a user_id that does not exist, and which constraint is this?

MySQL rejects the insert because the task references a user that does not exist in the `users` table. This is the **foreign-key constraint**, which enforces referential integrity.

### (c) Why do you store a hash and not the password?

Passwords should not be stored as plain text because someone who accesses the database could read them directly. Instead, the application stores a bcrypt password hash and verifies submitted passwords against it during login.

### (d) The name column is NOT NULL. Why is an additional check needed for an empty name?

`NOT NULL` prevents a database value from being SQL `NULL`, but it still allows an empty string or a string containing only spaces. The application must trim the input and check that the name contains actual characters.

## Conclusion

Taskly demonstrates how Flask, MySQL, and frontend technologies can be combined to build a web application with user authentication, secure database operations, and personal task management.
