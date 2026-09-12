from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from .models import EmailTemplate


class EmailOwnershipTests(APITestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(username="alice", password="password-123")
        self.user_b = User.objects.create_user(username="bob", password="password-123")
        self.client.force_authenticate(self.user_a)

    def test_user_can_only_see_own_templates(self):
        own = EmailTemplate.objects.create(
            owner=self.user_a, name="Own", subject="Hello", body="Hello"
        )
        EmailTemplate.objects.create(
            owner=self.user_b, name="Other", subject="Private", body="Private"
        )

        response = self.client.get("/api/emails/templates/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["id"] for item in response.data], [own.id])

    def test_created_template_belongs_to_current_user(self):
        response = self.client.post(
            "/api/emails/templates/",
            {"name": "Welcome", "subject": "Welcome", "body": "Hello {{ name }}"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["id"], EmailTemplate.objects.get(name="Welcome").id)
        self.assertEqual(EmailTemplate.objects.get(name="Welcome").owner_id, self.user_a.id)

    def test_cannot_create_message_with_someone_elses_template(self):
        template = EmailTemplate.objects.create(
            owner=self.user_b, name="Private", subject="Private", body="Private"
        )

        response = self.client.post(
            "/api/emails/messages/",
            {"template": template.id, "recipient": "test@example.com", "context": {}},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
