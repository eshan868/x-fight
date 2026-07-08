from django.shortcuts import render,redirect,get_object_or_404
from . forms import Tournament_Register_form,team_making_form
from . models import Tournament
# Create your views here.
def tournament_making(request):
    if request.POST:
        form=Tournament_Register_form(request.POST)
        if form.is_valid():
            tournament=form.save()
            tournament.save()
            return redirect("dashboard")
    else:
        form=Tournament_Register_form()
        print(form.errors)

    return render(request,"arena/forms/tournament_form.html",{"form":form})

def team_making(request):
    if request.POST:
        form=team_making_form(request.POST)
        if form.is_valid():
            team=form.save()
            team.save()
            return redirect("dashboard")
    else:
        form=team_making_form()
        print(form.errors)

    return render(request,"arena/forms/team_form.html",{"form":form})
def tournament_settings(request,event_id):
    tournament_details=get_object_or_404(Tournament,id=event_id)
    
    return render(request,"settings/tournament.html", {"event":tournament_details})


