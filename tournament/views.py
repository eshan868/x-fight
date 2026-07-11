from django.shortcuts import render,redirect,get_object_or_404
from . forms import Tournament_Register_form,team_making_form,match_making_form
from . models import Tournament,Team
from django.utils import timezone
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
            print("team created\n",team)
            return redirect("dashboard")
    else:
        form=team_making_form()
        print(form.errors)

    return render(request,"arena/forms/team_form.html",{"form":form})
def tournament_settings(request,event_id):
    tournament_details=get_object_or_404(Tournament,id=event_id)
    teams= tournament_details.team_set.all()
    matches=tournament_details.matches.filter(
        match_date__gte=timezone.now()
    )

    return render(request,"tournament/tournament_settings.html", {"event":tournament_details,"teams": teams,"matches":matches})

def tournament_dashboard(request,event_id):
    tournament=get_object_or_404(Tournament,id=event_id)
    teams=tournament.team_set.all()
    matches=tournament.matches.all()
    return render(request,'tournament/tournament_dashboard.html', {"events":tournament,"teams":teams,"matches":matches})

def match_creation(request,event_id):
    tournament = get_object_or_404(Tournament, id=event_id)
    
    if request.POST:
        form=match_making_form(request.POST)

        if form.is_valid():
            try:

                match=form.save(commit=False)
                match.tournament=tournament
                match.save()
                form.save_m2m()
            
                return redirect("event-management",event_id=event_id)
            except Exception as e:   
                print(e)
        else:
            print(form.non_field_errors)
    else:

        form=match_making_form()
        form.fields["teams"].queryset = Team.objects.filter(tournaments=tournament)

    return render(request,"arena/forms/match_form.html",{
        "form": form,
        "tournament": tournament, })



