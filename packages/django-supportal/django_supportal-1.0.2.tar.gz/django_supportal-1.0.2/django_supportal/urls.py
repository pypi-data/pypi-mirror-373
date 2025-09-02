from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api import views


app_name = "django_supportal"

router = DefaultRouter()
router.register(
    prefix=r"businesses",
    viewset=views.BusinessViewSet,
    basename="businesses",
)
router.register(
    prefix=r"documents",
    viewset=views.DocumentViewSet,
    basename="documents",
)
router.register(
    prefix=r"chat-sessions",
    viewset=views.ChatSessionViewSet,
    basename="chat-sessions",
)

urlpatterns = [
    path(
        route="api/",
        view=include(arg=router.urls),
    ),
    path(
        "create-session/<int:business_id>/",
        views.create_chat_session,
        name="create-session",
    ),
    path(
        "chats/<int:business_id>/<str:session_id>/",
        views.chat_interface,
        name="chat-interface",
    ),
    path(
        "admin-dashboard/",
        views.admin_dashboard,
        name="admin-dashboard",
    ),
    path(
        "health/",
        views.health_check,
        name="health-check",
    ),
]
