from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from .models import EmailMessage, EmailTemplate


User = get_user_model()


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class EmailMessageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="password-123")
        self.template = EmailTemplate.objects.create(
            owner=self.user,
            name="Welcome",
            subject="Welcome, {{ name }}",
            body="Hello {{ name }}!",
        )

    def test_send_task_renders_template_and_marks_message_sent(self):
        from .tasks import send_email_task

        message = EmailMessage.objects.create(
            template=self.template,
            recipient="user@example.com",
            context={"name": "Alex"},
        )

        result = send_email_task(message.id)

        message.refresh_from_db()
        self.assertEqual(result, "sent")
        self.assertEqual(message.status, EmailMessage.Status.SENT)
        self.assertEqual(message.attempts, 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Welcome, Alex")
        self.assertEqual(mail.outbox[0].body, "Hello Alex!")

    @patch("emails.tasks.EmailMultiAlternatives.send", side_effect=RuntimeError("SMTP unavailable"))
    def test_send_task_marks_message_failed_after_retries(self, _send):
        from .tasks import send_email_task

        message = EmailMessage.objects.create(
            template=self.template,
            recipient="user@example.com",
        )

        result = send_email_task.apply(args=[message.id]).get()

        message.refresh_from_db()
        self.assertEqual(result, "failed")
        self.assertEqual(message.status, EmailMessage.Status.FAILED)
        self.assertEqual(message.attempts, 4)
        self.assertEqual(message.error_message, "SMTP unavailable")


class EmailSchedulingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="password-123")
        self.template = EmailTemplate.objects.create(
            owner=self.user,
            name="Scheduled",
            subject="Reminder",
            body="Hello",
        )
        self.message = EmailMessage.objects.create(
            template=self.template,
            recipient="user@example.com",
            scheduled_at=timezone.now() + timedelta(minutes=10),
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    @patch("emails.views.send_email_task.apply_async")
    def test_future_message_uses_celery_eta(self, apply_async):
        response = self.client.post(f"/api/emails/messages/{self.message.id}/send/")

        self.assertEqual(response.status_code, 202)
        apply_async.assert_called_once()
        kwargs = apply_async.call_args.kwargs
        self.assertEqual(kwargs["args"], [self.message.id])
        self.assertEqual(kwargs["eta"], self.message.scheduled_at)

    @patch("emails.views.send_email_task.delay")
    def test_past_scheduled_message_sends_immediately(self, delay):
        self.message.scheduled_at = timezone.now() - timedelta(minutes=1)
        self.message.save(update_fields=["scheduled_at"])

        response = self.client.post(f"/api/emails/messages/{self.message.id}/send/")

        self.assertEqual(response.status_code, 202)
        delay.assert_called_once_with(self.message.id)
