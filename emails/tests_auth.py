from django.contrib.auth.models import User
from rest_framework.test import APITestCase


class AuthenticationTests(APITestCase):
    def test_register_and_login(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "alice",
                "email": "alice@example.com",
                "password": "strong-password-123",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username="alice").exists())

        response = self.client.post(
            "/api/auth/login/",
            {"username": "alice", "password": "strong-password-123"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
