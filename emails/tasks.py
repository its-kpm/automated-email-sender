from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.template import Context, Template
from django.utils import timezone

from .models import EmailMessage


@shared_task(bind=True, max_retries=3, retry_backoff=True)
def send_email_task(self, message_id):
    with transaction.atomic():
        message = (
            EmailMessage.objects.select_for_update()
            .select_related("template")
            .get(id=message_id)
        )
        if message.status == EmailMessage.Status.SENT:
            return "already-sent"
        message.attempts += 1
        message.save(update_fields=["attempts"])

    try:
        subject = Template(message.template.subject).render(Context(message.context))
        body = Template(message.template.body).render(Context(message.context))

        email = EmailMultiAlternatives(subject, body, to=[message.recipient])
        email.send(fail_silently=False)
    except Exception as exc:
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)

        message.status = EmailMessage.Status.FAILED
        message.error_message = str(exc)
        message.save(update_fields=["status", "error_message"])
        return "failed"

    message.status = EmailMessage.Status.SENT
    message.sent_at = timezone.now()
    message.error_message = ""
    message.save(update_fields=["status", "sent_at", "error_message"])
    return "sent"
