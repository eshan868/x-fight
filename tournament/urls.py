from django.urls import path
from . import views

urlpatterns=[
    path("tournament-creation/",views.tournament_making,name="tournament-creation"),
    path("team-creation/",views.team_making,name="team-creation")
    
]