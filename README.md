# Automated Email Sender

An intermediate Django REST Framework project for sending emails asynchronously with Celery and Redis.

## Stack

- Python 3.13+
- Django
- Django REST Framework
- PostgreSQL (SQLite works for local development)
- Redis
- Celery
- SMTP via Django email backend

## Features

- Reusable email templates
- Recipient-specific messages
- Template personalization with a JSON context
- Asynchronous email delivery with Celery
- Automatic retries with exponential backoff
- Delivery status and attempt tracking
- Django admin support
- Environment-based configuration

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

In a second terminal, start Redis and the Celery worker:

```bash
celery -A config worker --loglevel=info
```

The default email backend prints emails to the terminal. Add real SMTP settings to `.env` when you are ready to send real mail.

## API

Create a template:

```http
POST /api/emails/templates/
Content-Type: application/json

{
  "name": "Welcome",
  "subject": "Welcome, {{ name }}!",
  "body": "Hello {{ name }}, welcome to our service."
}
```

Create an email message:

```http
POST /api/emails/messages/
Content-Type: application/json

{
  "template": 1,
  "recipient": "user@example.com",
  "context": {"name": "Alex"}
}
```

Queue it for asynchronous delivery:

```http
POST /api/emails/messages/1/send/
```

The API returns `202 Accepted` after the Celery task is queued.

## Next milestones

1. JWT authentication and per-user ownership
2. Scheduled campaigns with Celery Beat
3. Bulk recipient imports
4. Rate limiting
5. Delivery webhooks and analytics
6. Automated tests and CI
