import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "lms_database.db")

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Add sample courses
courses = [
    ("Python Basics", "Learn Python from scratch."),
    ("Web Development", "HTML, CSS, JavaScript basics."),
    ("Data Science Intro", "Introduction to data science concepts."),
]

c.executemany("INSERT INTO courses (name, description) VALUES (?, ?)", courses)

# Add sample assignments
assignments = [
    (1, "Python Hello World", "2026-03-15"),
    (1, "Python Calculator", "2026-03-18"),
    (2, "Build a Personal Webpage", "2026-03-20"),
    (3, "Data Analysis Report", "2026-03-25"),
]

c.executemany("INSERT INTO assignments (course_id, title, due_date) VALUES (?, ?, ?)", assignments)

conn.commit()
conn.close()

print("Sample courses and assignments added!")