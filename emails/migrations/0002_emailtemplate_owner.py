from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def assign_existing_templates(apps, schema_editor):
    User = apps.get_model("auth", "User")
    EmailTemplate = apps.get_model("emails", "EmailTemplate")
    user = User.objects.order_by("id").first()
    if user:
        EmailTemplate.objects.filter(owner__isnull=True).update(owner=user)


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("emails", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="emailtemplate",
            name="owner",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="email_templates",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(assign_existing_templates, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="emailtemplate",
            name="owner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="email_templates",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
