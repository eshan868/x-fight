from django.shortcuts import render,get_object_or_404,redirect
from tournament.models import Tournament,Team
from django.contrib.auth.models import User


# Create your views here.

def event_display(request):
    user=request.user
    tournament=Tournament.objects.exclude(team__user=user).distinct()
    return render(request,"display/event_display.html",{"tournament":tournament})

def event_details(request,event_id): 
    tournament_details=get_object_or_404(Tournament,id=event_id)
    teams = Team.objects.filter(user=request.user)
    return render(request,"display/events_details.html", {"event":tournament_details,"team":teams})

def like(request,id):
    tournament=get_object_or_404(Tournament,id=id)
    user=request.user

    if tournament.like.filter(id=user.id).exists():
        tournament.like.remove(user)
        like=False
        
    else:
        tournament.like.add(user)
        like=True
    return redirect("events-display")

def home(request):
  

    return render(request,"home.html",)
        

