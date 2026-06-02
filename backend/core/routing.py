from django.urls import re_path
from core.consumers import LocationTrackingConsumer, GuardianNotificationConsumer

websocket_urlpatterns = [
    re_path(r'ws/location/(?P<session_id>[\w-]+)/$', LocationTrackingConsumer.as_asgi()),
    re_path(r'ws/guardian-notifications/$', GuardianNotificationConsumer.as_asgi()),
]
