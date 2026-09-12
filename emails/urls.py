from rest_framework.routers import DefaultRouter

from .views import EmailMessageViewSet, EmailTemplateViewSet

router = DefaultRouter()
router.register("templates", EmailTemplateViewSet, basename="email-template")
router.register("messages", EmailMessageViewSet, basename="email-message")

urlpatterns = router.urls
