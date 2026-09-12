from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="EmailTemplate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("subject", models.CharField(max_length=255)),
                ("body", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="EmailMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("recipient", models.EmailField(max_length=254)),
                ("context", models.JSONField(blank=True, default=dict)),
                ("status", models.CharField(choices=[("PENDING", "Pending"), ("SENT", "Sent"), ("FAILED", "Failed")], default="PENDING", max_length=20)),
                ("error_message", models.TextField(blank=True)),
                ("attempts", models.PositiveIntegerField(default=0)),
                ("scheduled_at", models.DateTimeField(blank=True, null=True)),
                ("sent_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("template", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="messages", to="emails.emailtemplate")),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
