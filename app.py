from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
from datetime import datetime
from groq import Groq

# Load environment variables
load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "supersecretkey"

# ------------------ Routes ------------------

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        conn = sqlite3.connect('lms_database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            session['fullname'] = user[1]
            return redirect(url_for('dashboard'))
        flash("Invalid email or password!")
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        password = request.form.get('password')
        conn = sqlite3.connect('lms_database.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (fullname, email, password) VALUES (?, ?, ?)",
                      (fullname, email, password))
            conn.commit()
            flash("Registration successful! Please login.")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Email already exists!")
        finally:
            conn.close()
    return render_template('register.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    fullname = session.get('fullname')
    conn = sqlite3.connect("lms_database.db")
    c = conn.cursor()

    # All courses
    c.execute("SELECT * FROM courses")
    courses = c.fetchall()

    # Compute progress for each course
    course_progress = {}
    for course in courses:
        course_id = course[0]
        c.execute("SELECT COUNT(*) FROM assignments WHERE course_id = ?", (course_id,))
        total_assignments = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM submissions WHERE user_id=? AND course_id=?",
                  (session['user_id'], course_id))
        submitted = c.fetchone()[0]

        progress = int((submitted / total_assignments) * 100) if total_assignments else 0
        course_progress[course_id] = progress

    conn.close()
    return render_template("dashboard.html", fullname=fullname, courses=courses, course_progress=course_progress)


@app.route('/courses')
def courses():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect("lms_database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM courses")
    all_courses = c.fetchall()
    c.execute("SELECT course_id FROM enrollments WHERE user_id=?", (session['user_id'],))
    enrolled = [row[0] for row in c.fetchall()]
    conn.close()
    return render_template("courses.html", courses=all_courses, enrolled=enrolled)


@app.route('/enroll/<int:course_id>')
def enroll(course_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('lms_database.db')
    c = conn.cursor()
    c.execute("INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)", (session['user_id'], course_id))
    conn.commit()
    conn.close()
    flash("Course added successfully!")
    return redirect(url_for('courses'))


@app.route('/course/<int:course_id>')
def course_detail(course_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect("lms_database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM courses WHERE id=?", (course_id,))
    course = c.fetchone()
    c.execute("SELECT * FROM assignments WHERE course_id=?", (course_id,))
    assignments = c.fetchall()
    conn.close()
    if not course:
        return "Course not found", 404
    return render_template("course_detail.html", course=course, assignments=assignments)


@app.route("/assignment", methods=["GET", "POST"])
def assignment():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("lms_database.db")
    c = conn.cursor()

    # Clear chat
    if request.args.get("clear") == "1":
        session["assignment_chat"] = []
        session.modified = True
        return redirect(url_for("assignment"))

    # Get enrolled courses
    c.execute("""
        SELECT courses.id, courses.name
        FROM courses
        JOIN enrollments ON courses.id = enrollments.course_id
        WHERE enrollments.user_id=?
    """, (session['user_id'],))
    courses = c.fetchall()

    submitted_file = None
    submission_time = None

    # Handle file submission
    if request.method == "POST" and "file" in request.files:
        course_id = request.form.get("course_id")
        file = request.files.get("file")
        if file and file.filename != "":
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            submitted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO submissions (user_id, course_id, filename, submitted_at) VALUES (?,?,?,?)",
                      (session["user_id"], course_id, filename, submitted_at))
            conn.commit()
            submitted_file = filename
            submission_time = submitted_at
            flash("Assignment submitted successfully!")

    # Fetch submissions
    c.execute("""
        SELECT submissions.id, courses.name, submissions.filename, submissions.submitted_at
        FROM submissions
        JOIN courses ON submissions.course_id = courses.id
        WHERE submissions.user_id=?
        ORDER BY submissions.submitted_at DESC
    """, (session["user_id"],))
    submissions = c.fetchall()
    conn.close()

    # AI chat
    if "assignment_chat" not in session:
        session["assignment_chat"] = []

    ai_response = None
    if request.method == "POST" and "question" in request.form:
        user_question = request.form.get("question")
        course_id = request.form.get("course_id")
        try:
            system_msg = "You are a helpful AI assistant for assignments."
            if course_id:
                system_msg += f" Student asking about course ID {course_id}."
            response = groq_client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[{"role": "system", "content": system_msg},
                          {"role": "user", "content": user_question}],
                max_tokens=500
            )
            ai_response = response.choices[0].message.content
        except Exception as e:
            ai_response = f"Error contacting AI: {str(e)}"

        session["assignment_chat"].append({"user": user_question, "ai": ai_response, "course_id": course_id})
        session.modified = True

    return render_template("assignment.html",
                           courses=courses,
                           filename=submitted_file,
                           submitted_at=submission_time,
                           submissions=submissions,
                           chat_history=session.get("assignment_chat", []))


@app.route("/ai", methods=["GET", "POST"])
def ai():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if "chat_history" not in session:
        session["chat_history"] = []

    # Clear chat
    if request.args.get("clear") == "1":
        session["chat_history"] = []
        session.modified = True
        return redirect(url_for("ai"))

    ai_response = None
    if request.method == "POST":
        user_question = request.form.get("question")
        course_id = request.form.get("course_id")
        try:
            system_msg = "You are a helpful AI study assistant."
            if course_id:
                system_msg += f" Student asking about course ID {course_id}."
            response = groq_client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[{"role": "system", "content": system_msg},
                          {"role": "user", "content": user_question}],
                max_tokens=500
            )
            ai_response = response.choices[0].message.content
        except Exception as e:
            ai_response = f"Error contacting AI: {str(e)}"

        session["chat_history"].append({"user": user_question, "ai": ai_response, "course_id": course_id})
        session.modified = True

    conn = sqlite3.connect("lms_database.db")
    c = conn.cursor()
    c.execute("""
        SELECT courses.id, courses.name
        FROM courses
        JOIN enrollments ON courses.id = enrollments.course_id
        WHERE enrollments.user_id=?
    """, (session["user_id"],))
    enrolled_courses = c.fetchall()
    conn.close()

    return render_template("ai_assistant.html",
                           chat_history=session["chat_history"],
                           courses=enrolled_courses)


@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("lms_database.db")
    c = conn.cursor()
    c.execute("SELECT fullname, email FROM users WHERE id=?", (session["user_id"],))
    user = c.fetchone()

    c.execute("""
        SELECT courses.name
        FROM courses
        JOIN enrollments ON courses.id = enrollments.course_id
        WHERE enrollments.user_id=?
    """, (session["user_id"],))
    courses = c.fetchall()

    c.execute("""
        SELECT courses.name, filename, submitted_at
        FROM submissions
        JOIN courses ON submissions.course_id = courses.id
        WHERE submissions.user_id=?
        ORDER BY submitted_at DESC
    """, (session["user_id"],))
    submissions = c.fetchall()
    conn.close()

    return render_template("profile.html", user=user, courses=courses, submissions=submissions)

@app.route("/add_course", methods=["POST"])
def add_course():
    if "user_id" not in session:
        return redirect(url_for("login"))

    course_name = request.form.get("course_name")
    course_desc = request.form.get("course_desc")

    if course_name and course_desc:
        conn = sqlite3.connect("lms_database.db")
        c = conn.cursor()
        c.execute("INSERT INTO courses (name, description) VALUES (?, ?)", (course_name, course_desc))
        conn.commit()
        conn.close()
        flash(f"Course '{course_name}' added successfully!")
    else:
        flash("Please provide both name and description.")

    return redirect(url_for("courses"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == '__main__':
    app.run(debug=True)