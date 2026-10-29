from django.shortcuts import render,get_object_or_404,redirect
from tournament.models import Tournament,Team
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import  timezone


# Create your views here.
@login_required
def event_display(request):
    current_time=timezone.now().date()
    user=request.user
    tournaments = (Tournament.objects.filter(end_time__gte=current_time).exclude(team__user=request.user).distinct())
    return render(request,"display/event_display.html",{"tournament":tournaments})

@login_required
def event_details(request,event_id): 
    tournament_details=get_object_or_404(Tournament,id=event_id)
    teams = Team.objects.filter(user=request.user)
    return render(request,"display/events_details.html", {"event":tournament_details,"team":teams})

@login_required
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

def about(request):
    return render(request,"layouts/about.html",)
        


        

