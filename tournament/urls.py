from django.urls import path
from . import views

urlpatterns=[
    path("tournament-creation/",views.tournament_making,name="tournament-creation"),
    path("team-creation/",views.team_making,name="team-creation"),
    path("event-settings/<int:event_id>/",views.tournament_settings,name="event-management"),
    path('tournament-dashboard/<int:event_id>/',views.tournament_dashboard,name="tournament-dashboard"),
    path('tournament=match-creation/<int:event_id>/',views.match_creation,name="match-creation"),
    path("match-room/<int:event_id>/<int:match_room_id>/",views.match_room,name="match-room"),
    path("match-room/<int:match_room_id>/",views.match_room,name="match-room"),
    path("match-report-submit/<int:match_id>/",views.match_scoreboard_form,name="match-scoreboard-form"),
    path("scoreboard/<int:event_id>/",views.scoreboard,name="scoreboard"),
    path("tournament/<int:event_id>/add-admin/",views.add_tournament_admin,name="add-tournament-admin"),
    path("tournament/<int:event_id>/remove-admin/",views.remove_tournament_admin,name="remove-tournament-admin"),
    path("team/<int:team_id>/",views.team_dashboard,name="team-dashboard"),
    path("team/add-member/<int:team_id>/",views.add_team_member,name="add-team-member"),
    path("team/remove-member/<int:team_id>/",views.remove_team_member,name="remove-team-member"),
    path("team/leave/<int:team_id>/",views.leave_team,name="leave-team"),
    path("team/vote-captain/<int:team_id>/",views.vote_team_captain,name="vote-team-captain"),
    path("team/schedule-meeting/<int:team_id>/",views.schedule_team_meeting,name="schedule-team-meeting"),
    path("team/meeting-room/<int:team_id>/<int:meeting_id>/",views.team_meeting_room,name="team-meeting-room"),
    path("tournament/join-page/<int:tournament_id>",views.tournament_join,name="tournament-join"),
    path('friendly-match-creation/',views.friendly_match_creation,name="friendly-match-creation"),

   
]