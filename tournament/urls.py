from django.urls import path
from . import views

urlpatterns=[
    path("tournament-making/",views.tournament_making,name="tournament-making"),
    
]