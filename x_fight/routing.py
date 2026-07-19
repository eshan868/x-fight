from django.urls import path
from tournament.consumers import *

websocket_urlpatterns=[
    path("tournament/<int:event_id>/",MatchroomConsumer.as_asgi()),
]