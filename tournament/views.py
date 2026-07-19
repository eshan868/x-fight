from django.shortcuts import render,redirect,get_object_or_404
from . forms import Tournament_Register_form,team_making_form,match_making_form
from . models import Tournament,Team,Match,match_player
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
    teams= tournament_details.team_set.prefetch_related("user").all()
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
                for team in match.teams.all():
                    for user in team.user.all():
                        match_player.objects.create(
                            match=match,
                            user=user,
                            ready=False
                        )

                    
                    
                print("match created ")
            
                return redirect("event-management",event_id=event_id)
            except Exception as e:  
                print(e)
        else:
            print(form.errors)
    else:

        form=match_making_form()
        form.fields["teams"].queryset = Team.objects.filter(tournaments=tournament)

    return render(request,"arena/forms/match_form.html",{
        "form": form,
        "tournament": tournament, })


def match_room(request, event_id, match_room_id):
    tournament = get_object_or_404(Tournament, id=event_id)
    match = get_object_or_404(Match, id=match_room_id)
    player=match.match_player.get(user=request.user)
    team = match.teams.filter(user=request.user).first()
    match_players = match.match_player.select_related("user").all()
    players=match.match_player.all()
    if player:
        if request.POST :
           
            action=request.POST.get("action")
            if action == "ready":
                print(player)
                player.ready=True
                player.save()
                #print("ready")
            else:
                player.ready=False
                player.save()
                
            player.refresh_from_db()
            if all(player.ready for player in players):
                match.status="live"

                
            print(player.ready)
    #print(match.id)
    #print("User:", request.user.username)
    #print("Team:", team)

    return render(request,"tournament/matches_display.html",{"tournament": tournament,"match": match,"team": team,"players":player,"match_players": match_players })