from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import EmailMessage, EmailTemplate
from .serializers import EmailMessageSerializer, EmailTemplateSerializer
from .tasks import send_email_task


class EmailTemplateViewSet(viewsets.ModelViewSet):
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer


class EmailMessageViewSet(viewsets.ModelViewSet):
    queryset = EmailMessage.objects.select_related("template").all()
    serializer_class = EmailMessageSerializer

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        message = self.get_object()
        if message.status == EmailMessage.Status.SENT:
            return Response({"detail": "Email has already been sent."}, status=status.HTTP_409_CONFLICT)

        send_email_task.delay(message.id)
        return Response({"id": message.id, "status": "QUEUED"}, status=status.HTTP_202_ACCEPTED)
