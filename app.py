import os
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///emails.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_USERNAME")

db = SQLAlchemy(app)
mail = Mail(app)
scheduler = BackgroundScheduler()


class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="PENDING")
    scheduled_at = db.Column(db.DateTime, nullable=True)
    sent_at = db.Column(db.DateTime, nullable=True)


def send_email(email_id):
    with app.app_context():
        email = db.session.get(Email, email_id)
        if not email or email.status == "SENT":
            return

        try:
            message = Message(
                subject=email.subject,
                recipients=[email.recipient],
                body=email.body,
            )
            mail.send(message)
            email.status = "SENT"
            email.sent_at = datetime.now()
        except Exception as exc:
            email.status = "FAILED"
            print(f"Email failed: {exc}")

        db.session.commit()


@app.route("/")
def home():
    emails = Email.query.order_by(Email.id.desc()).all()
    return render_template("index.html", emails=emails)


@app.route("/send", methods=["POST"])
def create_email():
    recipient = request.form.get("recipient", "").strip()
    subject = request.form.get("subject", "").strip()
    body = request.form.get("body", "").strip()
    scheduled_text = request.form.get("scheduled_at", "").strip()

    if not recipient or not subject or not body:
        flash("Recipient, subject and message are required.", "error")
        return redirect(url_for("home"))

    scheduled_at = None
    if scheduled_text:
        scheduled_at = datetime.fromisoformat(scheduled_text)

    email = Email(
        recipient=recipient,
        subject=subject,
        body=body,
        scheduled_at=scheduled_at,
    )
    db.session.add(email)
    db.session.commit()

    if scheduled_at and scheduled_at > datetime.now():
        scheduler.add_job(
            send_email,
            "date",
            run_date=scheduled_at,
            args=[email.id],
            id=f"email-{email.id}",
        )
        flash("Email scheduled successfully.", "success")
    else:
        send_email(email.id)
        flash("Email processed. Check the history for its status.", "success")

    return redirect(url_for("home"))


@app.route("/retry/<int:email_id>", methods=["POST"])
def retry_email(email_id):
    email = db.session.get(Email, email_id)
    if email:
        email.status = "PENDING"
        db.session.commit()
        send_email(email.id)
    return redirect(url_for("home"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    if not scheduler.running:
        scheduler.start()

    app.run(debug=True, use_reloader=False)
