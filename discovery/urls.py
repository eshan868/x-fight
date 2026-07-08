from django.urls import path
from . import views

urlpatterns=[
    path("events/",views.event_display,name="events-display"),
    path("event-detail/<int:event_id>/",views.event_details,name="event-details"),
    path("like/<int:id>/",views.like,name="like"),


]