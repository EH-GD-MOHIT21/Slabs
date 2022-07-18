from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/challenge/(?P<room_name>\w+)/$', consumers.ChallengeConsumer.as_asgi()),
]