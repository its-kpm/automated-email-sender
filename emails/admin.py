from django.contrib import admin

from .models import EmailMessage, EmailTemplate


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "subject", "created_at")
    search_fields = ("name", "subject")


@admin.register(EmailMessage)
class EmailMessageAdmin(admin.ModelAdmin):
    list_display = ("recipient", "template", "status", "attempts", "created_at", "sent_at")
    list_filter = ("status",)
    search_fields = ("recipient",)
