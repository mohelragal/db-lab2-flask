
import os
import re
from datetime import date
from functools import wraps

import bcrypt
import pymysql
from dotenv import load_dotenv
from flask import (
    Flask, flash, redirect, render_template,
    request, session, url_for,
)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv(
    "FLASK_SECRET_KEY", "development-only-change-me"
)


def get_db():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "registration"),
        cursorclass=pymysql.cursors.DictCursor,
        charset="utf8mb4",
        autocommit=True,
    )


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def email_looks_valid(email):
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email))


def validate_title(title):
    if not title:
        return ["Title is required"]
    if len(title) > 200:
        return ["Title is too long"]
    return []


def parse_due_date(value):
    if not value:
        return None
    return date.fromisoformat(value)


def prepare_todo(todo):
    due = todo.get("due_date")
    if hasattr(due, "date"):
        due = due.date()

    todo["is_overdue"] = bool(
        due and not todo["is_done"] and due < date.today()
    )
    todo["is_due_today"] = bool(
        due and not todo["is_done"] and due == date.today()
    )
    return todo


@app.route("/")
def index():
    return redirect(url_for("todos" if "user_id" in session else "login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    errors = {}
    name = ""
    email = ""

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name:
            errors["name"] = "Name is required"

        if not email:
            errors["email"] = "Email is required"
        elif not email_looks_valid(email):
            errors["email"] = "Please enter a valid email"

        if not password:
            errors["password"] = "Password is required"
        elif len(password.encode("utf-8")) > 72:
            errors["password"] = "Password must be at most 72 bytes"

        if not confirm_password:
            errors["confirm_password"] = "Confirm password is required"
        elif password != confirm_password:
            errors["confirm_password"] = "Passwords do not match"

        if errors:
            return render_template(
                "register.html", errors=errors,
                name=name, email=email
            ), 400

        password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        connection = get_db()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO users (email, name, pass_hash)
                       VALUES (%s, %s, %s)""",
                    (email, name, password_hash),
                )
                user_id = cursor.lastrowid
        except pymysql.err.IntegrityError:
            errors["email"] = "Email Already Exists"
            return render_template(
                "register.html", errors=errors,
                name=name, email=email
            ), 400
        finally:
            connection.close()

        session.clear()
        session["user_id"] = user_id
        session["name"] = name
        flash("Account created successfully!", "success")
        return redirect(url_for("todos"))

    return render_template(
        "register.html", errors=errors, name=name, email=email
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    errors = {}
    email = ""

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email:
            errors["email"] = "Email is required"
        if not password:
            errors["password"] = "Password is required"

        if errors:
            return render_template(
                "login.html", errors=errors, email=email
            ), 400

        connection = get_db()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT user_id, name, pass_hash
                       FROM users WHERE email = %s""",
                    (email,),
                )
                user = cursor.fetchone()
        finally:
            connection.close()

        password_ok = False
        if user:
            try:
                password_ok = bcrypt.checkpw(
                    password.encode("utf-8"),
                    user["pass_hash"].encode("utf-8"),
                )
            except (ValueError, TypeError):
                password_ok = False

        if not password_ok:
            errors["form"] = "Invalid email or password"
            return render_template(
                "login.html", errors=errors, email=email
            ), 401

        session.clear()
        session["user_id"] = user["user_id"]
        session["name"] = user["name"]
        return redirect(url_for("todos"))

    return render_template("login.html", errors=errors, email=email)


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/todos", methods=["GET", "POST"])
@login_required
def todos():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        due_value = request.form.get("due_date", "").strip()
        errors = validate_title(title)

        try:
            due_date = parse_due_date(due_value)
        except ValueError:
            due_date = None
            errors.append("Please enter a valid due date")

        if errors:
            for message in errors:
                flash(message, "error")
            return redirect(url_for("todos"))

        connection = get_db()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO todos (user_id, title, due_date)
                       VALUES (%s, %s, %s)""",
                    (session["user_id"], title, due_date),
                )
        finally:
            connection.close()

        flash("Task added successfully!", "success")
        return redirect(url_for("todos"))

    search_query = request.args.get("q", "").strip()
    status = request.args.get("status", "all")
    if status not in ("all", "open", "done"):
        status = "all"

    connection = get_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT todo_id, title, is_done, created_at, due_date
                   FROM todos
                   WHERE user_id = %s
                   ORDER BY todo_id DESC""",
                (session["user_id"],),
            )
            all_todos = cursor.fetchall()
    finally:
        connection.close()

    total_count = len(all_todos)
    completed_count = sum(bool(t["is_done"]) for t in all_todos)
    open_count = total_count - completed_count

    for todo in all_todos:
        prepare_todo(todo)

    visible_todos = all_todos

    if status == "open":
        visible_todos = [t for t in visible_todos if not t["is_done"]]
    elif status == "done":
        visible_todos = [t for t in visible_todos if t["is_done"]]

    if search_query:
        needle = search_query.casefold()
        visible_todos = [
            t for t in visible_todos
            if needle in t["title"].casefold()
        ]

    return render_template(
        "todos.html",
        todos=visible_todos,
        total_count=total_count,
        open_count=open_count,
        completed_count=completed_count,
        search_query=search_query,
        status=status,
    )


@app.route("/todos/<int:todo_id>/edit", methods=["POST"])
@login_required
def edit_todo(todo_id):
    title = request.form.get("title", "").strip()
    due_value = request.form.get("due_date", "").strip()
    errors = validate_title(title)

    try:
        due_date = parse_due_date(due_value)
    except ValueError:
        due_date = None
        errors.append("Please enter a valid due date")

    if errors:
        for message in errors:
            flash(message, "error")
        return redirect(url_for("todos"))

    connection = get_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """UPDATE todos
                   SET title = %s, due_date = %s
                   WHERE todo_id = %s AND user_id = %s""",
                (title, due_date, todo_id, session["user_id"]),
            )
            if cursor.rowcount == 0:
                cursor.execute(
                    """SELECT todo_id FROM todos
                       WHERE todo_id = %s AND user_id = %s""",
                    (todo_id, session["user_id"]),
                )
                if not cursor.fetchone():
                    flash("Task not found.", "error")
                    return redirect(url_for("todos"))
    finally:
        connection.close()

    flash("Task updated successfully.", "success")
    return redirect(url_for("todos"))


@app.route("/todos/<int:todo_id>/toggle", methods=["POST"])
@login_required
def toggle_todo(todo_id):
    done = 1 if request.form.get("is_done") == "1" else 0

    connection = get_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """UPDATE todos SET is_done = %s
                   WHERE todo_id = %s AND user_id = %s""",
                (done, todo_id, session["user_id"]),
            )
            if cursor.rowcount == 0:
                cursor.execute(
                    """SELECT todo_id FROM todos
                       WHERE todo_id = %s AND user_id = %s""",
                    (todo_id, session["user_id"]),
                )
                if not cursor.fetchone():
                    flash("Task not found.", "error")
                    return redirect(url_for("todos"))
    finally:
        connection.close()

    return redirect(url_for("todos"))


@app.route("/todos/<int:todo_id>/delete", methods=["POST"])
@login_required
def delete_todo(todo_id):
    connection = get_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """DELETE FROM todos
                   WHERE todo_id = %s AND user_id = %s""",
                (todo_id, session["user_id"]),
            )
            deleted = cursor.rowcount
    finally:
        connection.close()

    flash(
        "Task deleted successfully." if deleted else "Task not found.",
        "success" if deleted else "error",
    )
    return redirect(url_for("todos"))


if __name__ == "__main__":
    app.run(debug=True)