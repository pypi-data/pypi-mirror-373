from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(
        route=r"^ws/chat/(?P<business_id>\d+)/(?P<session_id>[^/]+)/$",
        view=consumers.ChatConsumer.as_asgi(),
    ),
]
