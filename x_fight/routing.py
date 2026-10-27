from django.urls import path
from tournament.consumers import *
from social.consumers import *

websocket_urlpatterns=[
    path("ws/chatroom/<str:chatroom_name>/", ChatConsumer.as_asgi()),
    path("ws/match/<int:match_id>/",MatchRoomConsumer.as_asgi()),
    path("ws/call/<str:call_id>/",CallConsumer.as_asgi(),),
    path("ws/call/<str:room_id>/",CallConsumer.as_asgi(),),
    path("ws/global-calls/",GlobalCallConsumer.as_asgi(),),

]