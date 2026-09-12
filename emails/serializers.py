from rest_framework import serializers

from .models import EmailMessage, EmailTemplate


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = ["id", "name", "subject", "body", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class EmailMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailMessage
        fields = [
            "id", "template", "recipient", "context", "status", "error_message",
            "attempts", "scheduled_at", "sent_at", "created_at",
        ]
        read_only_fields = ["id", "status", "error_message", "attempts", "sent_at", "created_at"]
