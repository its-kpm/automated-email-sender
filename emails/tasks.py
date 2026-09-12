from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.template import Template, Context
from django.utils import timezone

from .models import EmailMessage


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def send_email_task(self, message_id):
    with transaction.atomic():
        message = EmailMessage.objects.select_for_update().select_related("template").get(id=message_id)
        if message.status == EmailMessage.Status.SENT:
            return "already-sent"
        message.attempts += 1
        message.save(update_fields=["attempts"])

    subject = Template(message.template.subject).render(Context(message.context))
    body = Template(message.template.body).render(Context(message.context))

    email = EmailMultiAlternatives(subject, body, to=[message.recipient])
    email.send(fail_silently=False)

    message.status = EmailMessage.Status.SENT
    message.sent_at = timezone.now()
    message.error_message = ""
    message.save(update_fields=["status", "sent_at", "error_message"])
    return "sent"
