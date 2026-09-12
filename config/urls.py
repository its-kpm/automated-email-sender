from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("emails.auth_urls")),
    path("api/emails/", include("emails.urls")),
]
