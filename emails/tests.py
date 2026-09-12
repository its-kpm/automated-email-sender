from django.core import mail
from django.test import TestCase, override_settings

from .models import EmailMessage, EmailTemplate


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class EmailMessageTests(TestCase):
    def test_send_task_renders_template_and_marks_message_sent(self):
        from .tasks import send_email_task

        template = EmailTemplate.objects.create(
            name="Welcome",
            subject="Welcome, {{ name }}",
            body="Hello {{ name }}!",
        )
        message = EmailMessage.objects.create(
            template=template,
            recipient="user@example.com",
            context={"name": "Alex"},
        )

        result = send_email_task(message.id)

        message.refresh_from_db()
        self.assertEqual(result, "sent")
        self.assertEqual(message.status, EmailMessage.Status.SENT)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Welcome, Alex")
        self.assertEqual(mail.outbox[0].body, "Hello Alex!")
