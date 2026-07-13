from django.urls import path
from . import views

urlpatterns=[
    path("tournament-creation/",views.tournament_making,name="tournament-creation"),
    path("team-creation/",views.team_making,name="team-creation"),
    path("event-settings/<int:event_id>/",views.tournament_settings,name="event-management"),
    path('tournament-dashboard/<int:event_id>/',views.tournament_dashboard,name="tournament-dashboard"),
    path('tournament=match-creation/<int:event_id>/',views.match_creation,name="match-creation"),
    path("match-room/<int:event_id>/<int:match_room_id>/",views.match_room,name="match-room")
]