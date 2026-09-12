from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import EmailMessage, EmailTemplate
from .serializers import EmailMessageSerializer, EmailTemplateSerializer
from .tasks import send_email_task


class EmailTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = EmailTemplateSerializer

    def get_queryset(self):
        return EmailTemplate.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class EmailMessageViewSet(viewsets.ModelViewSet):
    serializer_class = EmailMessageSerializer

    def get_queryset(self):
        return EmailMessage.objects.select_related("template").filter(
            template__owner=self.request.user
        )

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        message = self.get_object()
        if message.status == EmailMessage.Status.SENT:
            return Response(
                {"detail": "Email has already been sent."},
                status=status.HTTP_409_CONFLICT,
            )
        if message.status == EmailMessage.Status.FAILED:
            return Response(
                {"detail": "Email delivery has permanently failed. Create a new message to retry."},
                status=status.HTTP_409_CONFLICT,
            )

        eta = message.scheduled_at
        if eta and eta <= timezone.now():
            eta = None

        if eta:
            send_email_task.apply_async(args=[message.id], eta=eta)
        else:
            send_email_task.delay(message.id)

        response = {"id": message.id, "status": "QUEUED"}
        if message.scheduled_at:
            response["scheduled_at"] = message.scheduled_at
        return Response(response, status=status.HTTP_202_ACCEPTED)
