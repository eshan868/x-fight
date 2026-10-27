from django.urls import path
from . import views

urlpatterns=[
    path("leaderboard/",views.leaderboard,name="leaderboard"),
    path("game-mate-request-sender/<int:user_id>/<int:mate_id>/",views.game_mate,name="game-mate"),
    path("game-mate-request-accept/<int:request_id>/",views.accept_game_mate,name="accept_game_mate"),
    path("game-mate-request-reject/<int:request_id>/",views.reject_game_mate,name="reject_game_mate"),
    path("chat/",views.chat_view,name="chat_view"),
    path('chat/<str:username>/',views.get_or_create_chatroom, name='start-chat'),
    path('chat/room/<str:chatroom_name>/',views.chat_view, name="chatroom"),
    path('chat/new-groupchat',views.create_groupchat, name="new-groupchat"),
    path('chat-group/detail/<str:chatgroup_room>',views.group_details, name='chat-group-detail'),
    path("chat-group/<str:group_name>/<int:mate_id>/invite/",views.send_group_invite,name="send-group-invite"),
    path("notifications/clear/",views.clear_all_notifications,name="clear_all_notifications"),
    path("chat/room/file-upload/<str:chatroom_name>/",views.chat_file_upload,name="chat-file-upload"),
    path("zego/token/", views.zego_token, name="zego_token"),
    path("calling/", views.calling_room, name="calling_room"),
    path("calls/start/",views.start_call,name="start_call"),
    path('stats/purchase',views.stats,name="stats-purchase")
    
]