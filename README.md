# Automated Email Sender - Flask

A beginner-friendly Python project for sending and scheduling emails from a simple web interface.

The project is intentionally small enough for a fresher to understand end-to-end, while still demonstrating Flask routes, forms, a database, SMTP email sending, scheduling, and basic error handling.

## Features

- Compose an email from the browser
- Send emails immediately
- Schedule emails for a future date/time
- Store email history in SQLite
- Track `PENDING`, `SENT`, and `FAILED` status
- Retry a failed email
- Simple responsive UI

## Tech Stack

- Python
- Flask
- Flask-Mail
- Flask-SQLAlchemy
- SQLite
- APScheduler
- HTML/CSS

## Project Structure

```text
automated-email-sender/
├── app.py
├── requirements.txt
├── .env.example
├── templates/
│   └── index.html
└── static/
    └── style.css
```

## Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/its-kpm/automated-email-sender.git
cd automated-email-sender
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows:

```bash
venv\\Scripts\\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure email credentials

```bash
cp .env.example .env
```

Edit `.env` and add your SMTP email and password. For Gmail, use a Google App Password rather than your normal account password.

### 5. Start the application

```bash
python app.py
```

Open `http://127.0.0.1:5000`.

## How It Works

1. The user fills in recipient, subject, message, and optionally a scheduled time.
2. Flask stores the email in SQLite.
3. Immediate emails are sent through SMTP using Flask-Mail.
4. Future emails are registered with APScheduler.
5. The email record is updated to `SENT` or `FAILED`.
6. Failed emails can be retried from the history table.

## Learning Goals

This project is useful for learning:

- Flask routing and forms
- SQLAlchemy models
- CRUD basics
- Environment variables
- SMTP email sending
- Simple task scheduling
- Error handling

## Note

The scheduler runs inside the Flask process, which is perfect for a learning project. A production system would normally use a separate task queue such as Celery or a managed scheduler.
