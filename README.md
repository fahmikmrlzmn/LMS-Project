# AI-Powered Learning Management System (LMS)

## Live Demo

You can try the deployed application here:

**Demo Link:**
https://lms-project-pdby.onrender.com/

This project is a cloud-deployed **AI-powered Learning Management System** built using **Flask** and hosted on **Render**.

The platform allows students to enroll in courses, submit assignments, track progress, and interact with an AI study assistant powered by **Groq**.

---

# Overview

This Learning Management System (LMS) provides a digital learning environment where students can manage coursework and receive AI-assisted learning support.

Learning Management Systems are widely used in education to support online learning, course management, and assignment submission workflows. ([fyphub.shop][1])

The system demonstrates practical skills in:

* Full-stack web development
* Database management
* AI integration
* Cloud deployment
* Educational technology design

---

# Core Features

## User Authentication

* User registration
* Secure login system
* Session-based authentication
* Logout functionality

## Student Dashboard

The dashboard provides an overview of:

* Enrolled courses
* Course progress
* Quick navigation to assignments and AI tools

## Course Enrollment

Students can:

* Browse available courses
* Enroll in courses
* Access course details and assignments

## Assignment Submission

The platform supports:

* File uploads for assignments
* Secure file handling
* Submission history
* Timestamped assignment tracking

## AI Study Assistant

The built-in AI assistant allows students to:

* Ask study questions
* Get explanations for course topics
* Receive learning guidance

This feature is powered by **Groq AI models**.

## AI Assignment Support

Students can also ask AI for help with assignments directly from the assignment page.

The assistant can:

* Explain assignment questions
* Provide hints
* Guide problem solving

## AI Quiz Generator

Students can generate practice quizzes based on specific topics to improve their understanding.

## Leaderboard

A leaderboard ranks students based on assignment submissions to encourage engagement and participation.

## Student Profile

Each student has a profile page that shows:

* Personal information
* Enrolled courses
* Assignment submission history

---

# Technology Stack

### Backend

* Python
* **Flask**
* SQLite database

### Frontend

* HTML
* CSS
* JavaScript
* Jinja2 templates

### AI Integration

* **Groq API**

### Deployment

* Hosted on **Render cloud platform**

---

# Project Structure

```
LMS-Project
│
├── app.py
├── requirements.txt
├── lms_database.db
│
├── templates
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── courses.html
│   ├── course_detail.html
│   ├── assignment.html
│   ├── ai_assistant.html
│   └── profile.html
│
├── static
│   ├── style.css
│   └── script.js
│
└── uploads
```

---

# Installation

## Clone the repository

```
git clone https://github.com/yourusername/lms-project.git
cd lms-project
```

## Install dependencies

```
pip install -r requirements.txt
```

## Set environment variable

Create `.env` file:

```
GROQ_API_KEY=your_api_key_here
```

## Run the application

```
python app.py
```

Open in browser:

```
http://127.0.0.1:5000
```

---

# Deployment

This project is deployed on **Render**.

Deployment configuration:

Build Command:

```
pip install -r requirements.txt
```

Start Command:

```
gunicorn app:app
```

Environment variable required:

```
GROQ_API_KEY=your_api_key
```

---

# Author

**Muhd Fahmi**
Bachelor of Computer Science (Hons.)
Universiti Teknologi PETRONAS (2024–2027)

---

# License

This project is intended for educational and portfolio purposes.

[1]: https://www.fyphub.shop/projects/learning-management-system-lms?utm_source=chatgpt.com "Learning Management System (LMS) - pkr3499 | FYP Hub"
