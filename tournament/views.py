from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from . forms import *
from . models import *
from django.utils import timezone
from . report_analyzing_ai.main import match_data,analyze_match
from .report_analyzing_ai.game_models import *
import json
import os 
from social.models import ChatGroup, ChatGroupMessages
from social.forms import ChatMessageCreatorForm
from django.http import JsonResponse,HttpResponseBadRequest
from django.urls import reverse
from django.contrib import messages
from accounts.models import user_profile
from django.db import transaction
import random 
import json 
import re
# Create your views here.
with open("match_result.json", "r") as f:
    data = json.load(f)

captain_elections = {}
@login_required
def tournament_making(request):
    if request.POST:
        form=Tournament_Register_form(request.POST)
        if form.is_valid():
            tournament=form.save()
            tournament.owner=request.user
            tournament.players.add(request.user)
            tournament.save()
            return redirect("dashboard")
    else:
        form=Tournament_Register_form()
        print(form.errors)

    return render(request,"arena/forms/tournament_form.html",{"form":form})
@login_required
def team_making(request):

    if request.method == "POST":

        form = team_making_form(
            request.POST,
            request.FILES,
            user=request.user
        )

        if form.is_valid():
            
            team = form.save(commit=False)
            team.captain = request.user
            team.save()
            team.user.add(request.user)
        
            print("team created\n", team)
            return redirect("dashboard")

    else:

        form = team_making_form(
            user=request.user
        )

    return render(request,"arena/forms/team_form.html",{"form": form })




@login_required
def team_dashboard(request, team_id):

    team = get_object_or_404(Team,id=team_id)
    

    # --------------------------------------------------------
    # CHECK MEMBER
    # --------------------------------------------------------

    if not team.user.filter(
        id=request.user.id
    ).exists():

        messages.error(
            request,
            "You are not a member of this team."
        )

        return redirect("dashboard")

    # --------------------------------------------------------
    # CAPTAIN
    # --------------------------------------------------------

    is_captain = (
        team.captain_id == request.user.id
    )

    # --------------------------------------------------------
    # MEMBERS
    # --------------------------------------------------------

    members = team.user.all()

    team_chat, created = ChatGroup.objects.get_or_create(
        team=team,
        defaults={
            "groupchat_name": f"{team.name} Chat",
            "is_private": False,
        }
    )

    # Keep team members connected to the chat
    team_chat.members.add(*members)

    # Add the captain as an admin, if applicable
    if is_captain:
        team_chat.admin.add(request.user)

    team_chat_messages = ChatGroupMessages.objects.filter(
        group=team_chat
    )

    # --------------------------------------------------------
    # GAME MATES
    # --------------------------------------------------------

    relations = GameMate.objects.filter(
        Q(
            user=request.user,
            status="accepted"
        )
        |
        Q(
            mate=request.user,
            status="accepted"
        )
    )

    game_mates = []

    for relation in relations:

        if relation.user_id == request.user.id:

            game_mates.append(
                relation.mate
            )

        else:

            game_mates.append(
                relation.user
            )

    # --------------------------------------------------------
    # TEAM TOURNAMENTS
    # --------------------------------------------------------

    tournaments = team.tournaments.all()

    # --------------------------------------------------------
    # UPCOMING MATCHES
    # --------------------------------------------------------

    upcoming_matches = Match.objects.filter(
        teams=team
    ).exclude(
        status="finished"
    ).order_by(
        "match_start_time"
    )

    # --------------------------------------------------------
    # TEAM MEETINGS
    # --------------------------------------------------------

    meetings = team_meeting.objects.filter(
        team=team
    ).order_by(
        "start_time"
    )

    now = timezone.now()

    for meeting in meetings:

        start_time = meeting.start_time
        end_time = meeting.end_time

        if  end_time and start_time and now >= start_time  and now < end_time:
            meeting.status = "active"
        elif  end_time and now >= end_time:
            meeting.status = "finished"
        else:
            meeting.status="waiting"




      
        # ----------------------------------------------------
        # ZEGO ROOM ID
        # ----------------------------------------------------

        meeting.room_id = (
            f"x_fight_team_"
            f"{team.id}_meeting_"
            f"{meeting.id}"
        )

    # --------------------------------------------------------
    # ELECTION
    # --------------------------------------------------------

    votes = captain_elections.get(
        team.id,
        {}
    )

    has_voted = (
        request.user.id in votes
    )

    total_votes = len(votes)

    total_members = team.user.count()

    # --------------------------------------------------------
    # VOTE COUNTS
    # --------------------------------------------------------

    vote_counts = {}

    for candidate_id in votes.values():

        vote_counts[candidate_id] = (
            vote_counts.get(
                candidate_id,
                0
            ) + 1
        )

    # --------------------------------------------------------
    # RENDER
    # --------------------------------------------------------

    return render(
        request,
        "user/team_dashboard.html",
        {
            "team": team,
            "members": members,
            "game_mates": game_mates,
            "tournaments": tournaments,
            "upcoming_matches": upcoming_matches,
            "is_captain": is_captain,
            "meetings": meetings,
            "total_members": total_members,
            "has_voted": has_voted,
            "total_votes": total_votes,
            "vote_counts": vote_counts,
            "team_chat": team_chat,
            "team_chat_messages": team_chat_messages,
            "chat_form": ChatMessageCreatorForm(),
        }
    )
# =========================================================
# ADD TEAM MEMBER
# =========================================================

temporary_meetings = {}


@login_required
def schedule_team_meeting(request, team_id):
    form=team_meeting_schedule_form()
    team=get_object_or_404(Team,id=team_id)
    if request.method == "POST":
        form=team_meeting_schedule_form(request.POST)
        if form.is_valid():
            team_meeting=form.save(commit=False)
            team_meeting.team=team
            team_meeting.save()
            return redirect("team-dashboard" ,team_id)

    return render(request,"arena/forms/team_meeting_schedule.html", {"form":form})

@login_required
def add_team_member(request, team_id):

    team = get_object_or_404(
        Team,
        id=team_id
    )

    # ==========================================
    # ONLY CAPTAIN
    # ==========================================

    if team.captain_id != request.user.id:

        messages.error(
            request,
            "Only the team captain can add members."
        )

        return redirect(
            "team-dashboard",
            team_id=team.id
        )

    if request.method != "POST":

        return redirect(
            "team-dashboard",
            team_id=team.id
        )

    user_id = request.POST.get(
        "user_id"
    )

    if not user_id:

        messages.error(
            request,
            "No Game Mate was selected."
        )

        return redirect(
            "team-dashboard",
            team_id=team.id
        )

    user = get_object_or_404(
        User,
        id=user_id
    )

    # ==========================================
    # ALREADY MEMBER?
    # ==========================================

    if team.user.filter(
        id=user.id
    ).exists():

        messages.warning(
            request,
            f"{user.username} is already a team member."
        )

        return redirect(
            "team-dashboard",
            team_id=team.id
        )

    # ==========================================
    # MAXIMUM PLAYERS
    # ==========================================

    if team.user.count() >= team.max_players:

        messages.error(
            request,
            "The team has reached its maximum player limit."
        )

        return redirect(
            "team-dashboard",
            team_id=team.id
        )

    # ==========================================
    # CHECK GAMEMATE
    # ==========================================

    is_game_mate = GameMate.objects.filter(
        Q(
            user=request.user,
            mate=user
        )
        |
        Q(
            user=user,
            mate=request.user
        ),
        status="accepted"
    ).exists()

    if not is_game_mate:

        messages.error(
            request,
            "You can only add your accepted Game Mates."
        )

        return redirect(
            "team-dashboard",
            team_id=team.id
        )

    # ==========================================
    # ADD MEMBER
    # ==========================================

    team.user.add(request.user)
    team.team_chat.members.add(request.user)
    messages.success(
        request,
        f"{user.username} was added to the team."
    )

    return redirect(
        "team-dashboard",
        team_id=team.id
    )


@login_required
def remove_team_member(request, team_id):

    team = get_object_or_404(
        Team,
        id=team_id
    )

    # ==========================================
    # ONLY CAPTAIN
    # ==========================================

    if team.captain_id != request.user.id:

        messages.error(
            request,
            "Only the team captain can remove members."
        )

        return redirect(
            "team-dashboard",
            team_id=team.id
        )

    if request.method != "POST":

        return redirect(
            "team-dashboard",
            team_id=team.id
        )

    user_id = request.POST.get(
        "user_id"
    )

    if not user_id:

        messages.error(
            request,
            "No member selected."
        )

        return redirect(
            "team-dashboard",
            team_id=team.id
        )

    user = get_object_or_404(
        User,
        id=user_id
    )

    # ==========================================
    # CANNOT REMOVE CAPTAIN
    # ==========================================

    if user.id == team.captain_id:

        messages.error(
            request,
            "The captain cannot be removed."
        )

        return redirect(
            "team-dashboard",
            team_id=team.id
        )

    # ==========================================
    # CHECK MEMBER
    # ==========================================

    if not team.user.filter(
        id=user.id
    ).exists():

        messages.error(
            request,
            "This user is not a member of the team."
        )

        return redirect(
            "team-dashboard",
            team_id=team.id
        )

    # ==========================================
    # REMOVE
    # ==========================================
    team.user.remove(request.user)

    team.team_chat.members.remove(request.user)  

    # Remove this user's old vote if an election exists
    if team.id in captain_elections:

        captain_elections[
            team.id
        ].pop(
            user.id,
            None
        )

    messages.success(
        request,
        f"{user.username} was removed from the team."
    )

    return redirect(
        "team-dashboard",
        team_id=team.id
    )


@login_required
def leave_team(request, team_id):

    team = get_object_or_404(
        Team,
        id=team_id
    )

    if request.method != "POST":

        return redirect(
            "team-dashboard",
            team_id=team.id
        )

    # ==========================================
    # CHECK MEMBER
    # ==========================================

    if not team.user.filter(
        id=request.user.id
    ).exists():

        messages.error(
            request,
            "You are not a member of this team."
        )

        return redirect("dashboard")

    # ==========================================
    # CAPTAIN CANNOT LEAVE
    # ==========================================

    if team.captain_id == request.user.id:

        messages.error(
            request,
            "The captain cannot leave. Elect a new captain first."
        )

        return redirect(
            "team-dashboard",
            team_id=team.id
        )

    # ==========================================
    # REMOVE USER
    # ==========================================

    team.user.remove(request.user)

    team.team_chat.members.remove(request.user)

    # Remove vote if exists
    if team.id in captain_elections:

        captain_elections[
            team.id
        ].pop(
            request.user.id,
            None
        )

    messages.success(
        request,
        "You left the team."
    )

    return redirect(
        "dashboard"
    )


# =========================================================
# VOTE FOR NEW CAPTAIN
# =========================================================
@login_required
def vote_team_captain(request, team_id):

    team = get_object_or_404(
        Team,
        id=team_id
    )

    if request.method != "POST":

        return redirect(
            "team-dashboard",
            team_id=team.id
        )

    # ==========================================
    # CHECK MEMBER
    # ==========================================

    if not team.user.filter(
        id=request.user.id
    ).exists():

        messages.error(
            request,
            "Only team members can vote."
        )

        return redirect("dashboard")

    # ==========================================
    # CHECK WHETHER ALREADY VOTED
    # ==========================================

    if team.id not in captain_elections:

        captain_elections[
            team.id
        ] = {}

    votes = captain_elections[
        team.id
    ]

    if request.user.id in votes:

        messages.error(
            request,
            "You have already voted."
        )

        return redirect(
            "team-dashboard",
            team_id=team.id
        )

    # ==========================================
    # GET CANDIDATE
    # ==========================================

    candidate_id = request.POST.get(
        "candidate_id"
    )

    if not candidate_id:

        messages.error(
            request,
            "Please select a candidate."
        )

        return redirect(
            "team-dashboard",
            team_id=team.id
        )

    candidate = get_object_or_404(
        User,
        id=candidate_id
    )

    # ==========================================
    # CANDIDATE MUST BE MEMBER
    # ==========================================

    if not team.user.filter(
        id=candidate.id
    ).exists():

        messages.error(
            request,
            "That user is not a member of this team."
        )

        return redirect(
            "team-dashboard",
            team_id=team.id
        )

    # ==========================================
    # CANNOT VOTE FOR YOURSELF
    # ==========================================

    if candidate.id == request.user.id:

        messages.error(
            request,
            "You cannot vote for yourself."
        )

        return redirect(
            "team-dashboard",
            team_id=team.id
        )

    # ==========================================
    # SAVE TEMPORARY VOTE
    # ==========================================

    votes[
        request.user.id
    ] = candidate.id

    # ==========================================
    # CHECK EVERYONE HAS VOTED
    # ==========================================

    total_members = team.user.count()

    total_votes = len(votes)

    if total_votes >= total_members:

        # ======================================
        # COUNT VOTES
        # ======================================

        vote_counts = {}

        for candidate_id in votes.values():

            vote_counts[candidate_id] = (
                vote_counts.get(candidate_id, 0) + 1
            )

        # ======================================
        # FIND HIGHEST NUMBER
        # ======================================

        highest_votes = max(
            vote_counts.values()
        )

        winners = [
            candidate_id
            for candidate_id, count
            in vote_counts.items()
            if count == highest_votes
        ]

        # ======================================
        # CLEAR WINNER
        # ======================================

        if len(winners) == 1:

            new_captain = get_object_or_404(
                User,
                id=winners[0]
            )

            team.captain = new_captain
            team.save()

            messages.success(
                request,
                f"👑 {new_captain.username} is now the team captain!"
            )

            # Clear temporary election
            del captain_elections[
                team.id
            ]

        # ======================================
        # TIE
        # ======================================

        else:

            messages.warning(
                request,
                "The election ended in a tie. A new election will begin."
            )

            del captain_elections[
                team.id
            ]

    else:

        messages.success(
            request,
            "Your vote has been recorded."
        )

    return redirect(
        "team-dashboard",
        team_id=team.id
    )
@login_required
def tournament_settings(request, event_id):

    tournament_details = get_object_or_404(
        Tournament,
        id=event_id
    )

    teams = tournament_details.team_set.all()

    matches = tournament_details.matches.all()
    players=tournament_details.players.all()


    game_mate_requests = GameMate.objects.filter(
        Q(user=request.user) | Q(mate=request.user),
        status="accepted"
    )


    game_mates = []

    for gm in game_mate_requests:

        if gm.user == request.user:

            game_mates.append(gm.mate)

        else:

            game_mates.append(gm.user)

    event_admins = tournament_details.admins.all()


    return render(request,"tournament/tournament_settings.html",{"event": tournament_details,"teams": teams,"matches": matches,"game_mates": game_mates,"event_admins": event_admins,"players":players})
@login_required
def add_tournament_admin(request, event_id):

    tournament = get_object_or_404(
        Tournament,
        id=event_id
    )
    if tournament.owner != request.user:
        messages.error(
            request,
            "Only the tournament owner can add admins."
        )
        return redirect(
            "event-management",
            event_id=event_id
        )

    if request.method != "POST":
        return redirect(
            "event-management",
            event_id=event_id
        )


    user_id = request.POST.get("user_id")


    if not user_id:
        messages.error(
            request,
            "No user was selected."
        )
        return redirect(
            "event-management",
            event_id=event_id
        )
    user = get_object_or_404(
        User,
        id=user_id
    )
    if user == tournament.owner:

        messages.warning(
            request,
            "The tournament owner is already the owner."
        )
        return redirect(
            "event-management",
            event_id=event_id
        )

    is_game_mate = GameMate.objects.filter(Q(user=request.user, mate=user)|Q(user=user,mate=request.user),status="accepted").exists()

    if not is_game_mate:

        messages.error(
            request,
            "You can only add an accepted Game Mate as an admin."
        )

        return redirect(
            "event-management",
            event_id=event_id
        ) 

    tournament.admins.add(user)

    messages.success(
        request,
        f"{user.username} was added as a tournament admin."
    )

    return redirect(
        "event-management",
        event_id=event_id
    )
@login_required
def remove_tournament_admin(request, event_id):

    tournament = get_object_or_404(
        Tournament,
        id=event_id
    )
    if tournament.owner != request.user:

        messages.error(
            request,
            "Only the tournament owner can remove admins."
        )

        return redirect(
            "event-management",
            event_id=event_id
        )

    if request.method != "POST":

        return redirect(
            "event-management",
            event_id=event_id
        )
    user_id = request.POST.get("user_id")
    if not user_id:

        messages.error(
            request,
            "No admin was selected."
        )
        return redirect(
            "event-management",
            event_id=event_id
        )

    user = get_object_or_404(
        User,
        id=user_id
    )

    if user == tournament.owner:

        messages.error(
            request,
            "The tournament owner cannot be removed."
        )
        return redirect(
            "event-management",
            event_id=event_id
        )

    tournament.admins.remove(user)

    messages.success(
        request,
        f"{user.username} was removed as tournament admin."
    )

    return redirect(
        "event-management",
        event_id=event_id
    )
@login_required
def tournament_dashboard(request,event_id):

    tournament=get_object_or_404(Tournament,id=event_id)
    teams=tournament.team_set.all()
    matches=tournament.matches.all()
    players=tournament.players.all()



    for match in matches:

        if tournament.category == "team":
            match.user_is_participant = match.teams.filter(
                user=request.user
            ).exists()

        elif tournament.category == "solo":
            match.user_is_participant = match.match_players.filter(
                id=request.user.id
            ).exists()

        else:
            match.user_is_participant = False
    return render(request,'tournament/tournament_dashboard.html', {"event":tournament,"teams":teams,"matches":matches,"players":players})
@login_required
def team_meeting_room(request,team_id,meeting_id):
    team=get_object_or_404(Team,id=team_id)
    meeting=get_object_or_404(team_meeting,id=meeting_id)

    return render(request,"user/team_meeting.html",{"team":team,"meeting":meeting})
@login_required
def match_creation(request, event_id):

    tournament = get_object_or_404(
        Tournament,
        id=event_id
    )
    form = match_making_form(request.POST or None)
    if tournament.category == "team":
            form.fields["teams"].queryset = Team.objects.filter(tournaments=tournament)
                
    elif tournament.category == "solo":
            form.fields["match_players"].queryset = tournament.players.all()
            print(tournament.players.all())

    

    if request.method == "POST":

        if form.is_valid():

            try:
                match = form.save(commit=False)

                match.tournament = tournament
                match.save()
                form.save_m2m()

                if tournament.category == "team":

                    for team in match.teams.all():

                        for user in team.user.all():

                            match_player.objects.create(
                                match=match,
                                user=user,
                                team=team,
                                ready=False
                            )

                elif tournament.category == "solo":

                    for player in match.match_players.all():

                        match_player.objects.create(
                            match=match,
                            user=player,
                            ready=False
                        )

                print("match created")

                return redirect(
                    "event-management",
                    event_id=event_id
                )

            except Exception as e:
                print(e)

        else:
            print(form.errors)
            

    return render(
        request,
        "arena/forms/match_form.html",
        {
            "form": form,
            "tournament": tournament,
        }
    )
@login_required
def match_room(request, match_room_id, event_id=None):

    match = get_object_or_404(Match,id=match_room_id)
    is_friendly = match.friendly_match_room
    tournament = None
    if not is_friendly:
        if not event_id:
            return HttpResponseBadRequest("Tournament match requires an event ID." )
        tournament = get_object_or_404( Tournament,id=event_id)

    team = match.teams.filter(user=request.user).first()
    player = match.match_player.filter(user=request.user).first()
    match_players = match.match_player.select_related("user","team").all()
    players = match.match_player.all()
    friendly_players = []
    match_result_exists = match_result_form.objects.filter(match=match).exists()

    if is_friendly:

        for player in match.match_players.all():

            match_player = match.match_player.filter(
                user=player
            ).first()

            friendly_players.append({
                "user": player,
                "match_player": match_player,
            })
        
        if match_result_exists:
            match_result=get_object_or_404(match_result_form,match=match)
            report_upload_player=match_result.player
        
        else:
            report_upload_player_selected = random.choice(friendly_players) 
            match_result_form.objects.create(match=match,player=report_upload_player_selected['user'])
            match_result=get_object_or_404(match_result_form,match=match)
            report_upload_player=match_result.player
            
        print("upload user",report_upload_player.username)


        

        

    team_data = []

    if not is_friendly:

        for match_team in match.teams.all():

            team_players = []

            for user in match_team.user.all():

                match_player = match.match_player.filter(
                    user=user
                ).first()

                team_players.append({

                    "user": user,

                    "match_player": match_player,

                })

            team_data.append({

                "team": match_team,

                "players": team_players,

            })

    can_upload_report = False

    return render(
        request,
        "tournament/match_room.html",
        {
            "tournament": tournament,

            "match": match,

            "team": team,

            "player": player,

            "match_players": match_players,

            "players": players,

            "team_data": team_data,

            "friendly_players": friendly_players,

            "is_friendly": is_friendly,

            "can_upload_report": can_upload_report,

            "report_upload_player":report_upload_player
        }
    )
@login_required
def match_scoreboard_form(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    is_freindly = match.friendly_match_room
    report = get_object_or_404(match_result_form,match=match,player=request.user)
    if request.method == "POST":
        form = MatchScoreboardForm( request.POST, request.FILES, instance=report)
        if form.is_valid():
            
            print("FORM ERRORS:", form.errors)

            if report.screenshot:
                return JsonResponse({
                    "success": False,
                    "error": "You have already submitted  a report for this match.",
            }, status=400)

            match_result=form.save(commit=False)
            match_result.match=match
            match_result.save()
            info = match_data(match.id)
            game=match.game.lower()
            result_file = "match_result.json"
            if os.path.exists(result_file):
                with open(result_file, "r") as f:
                    try:
                        matches = json.load(f)
                    except json.JSONDecodeError:
                        matches = []
            else:
                matches = []
            found = any(match["match_id"] == match_id for match in matches)


            if not found :
                if game == "efootball" :
                    response = e_footbll(info["image"])
                elif game == "fc football":
                    response = fc_football(info["image"])
                elif game == "other":
                    response = other(info["image"])
                else:
                    response = other(info["image"])

                

                try:
                    analyze_match(info, response)
                except Exception as e:
                    print(f"data insert error {e} ")
                
            
            else:
                print("match aldready analyzed")
            

            return JsonResponse({
                                "success": True,
                                "redirect": reverse(
                                    "match-room",
                                    kwargs={
                                        "match_room_id": match.id,
                                    },
                                ),
                            })
        else:
            print("FORM ERRORS:", form.errors)
            print("POST DATA:", request.POST)
            print("FILES:", request.FILES)
    else:
        form = MatchScoreboardForm(instance=report)

    return render(request,"arena/forms/match_report_form.html",{"form": form,"match": match})

@login_required
def scoreboard(request, event_id):
    with open("match_result.json", "r") as f:
        data = json.load(f)

    data = [
        item
        for item in data
        if item.get("tournament_id") == event_id
    ]

    matches = []

    for item in data:
        matches.append(
            get_object_or_404(
                Match,
                id=item["match_id"]
            )
        )




    return render(request,"tournament/scoreboard.html",{"data":data,"match":matches})


@login_required
def tournament_join(request, tournament_id):

    tournament = get_object_or_404(
        Tournament,
        id=tournament_id
    )

    teams = Team.objects.filter(
        user=request.user
    )

    def render_join_page(error=None, success=None):

        return render(
            request,
            "tournament/join_page.html",
            {
                "tournament": tournament,
                "teams": teams,
                "error": error,
                "success": success,
            }
        )

    # -----------------------------------------
    # POST REQUEST
    # -----------------------------------------

    if request.method == "POST":

        selected_team = None

        # -----------------------------------------
        # TEAM TOURNAMENT
        # -----------------------------------------

        if tournament.category == "team":

            team_id = request.POST.get("team_id")

            if not team_id:

                return render_join_page(
                    error="Please select a team."
                )

            try:

                selected_team = Team.objects.get(
                    id=team_id,
                    user=request.user
                )

            except Team.DoesNotExist:

                return render_join_page(
                    error="The selected team is invalid or you are not a member of that team."
                )

            # Prevent duplicate team registration

            if selected_team.tournaments.filter(
                id=tournament.id
            ).exists():

                return render_join_page(
                    error="This team has already joined the tournament."
                )

        # -----------------------------------------
        # SOLO TOURNAMENT
        # -----------------------------------------

        else:

            if tournament.players.filter(
                id=request.user.id
            ).exists():

                return render_join_page(
                    error="You have already joined this tournament."
                )

        # -----------------------------------------
        # ENTRY FEE VALIDATION
        # -----------------------------------------

        try:

            entry_fee = int(
                tournament.entry_fee or 0
            )

        except (TypeError, ValueError):

            return render_join_page(
                error="Invalid tournament entry fee."
            )

        if entry_fee < 0:

            return render_join_page(
                error="Entry fee cannot be negative."
            )

        # -----------------------------------------
        # PAYMENT + REGISTRATION
        # -----------------------------------------

        with transaction.atomic():

            # Lock the user's profile during coin deduction

            profile = user_profile.objects.select_for_update().get(
                user=request.user
            )

            # Check balance for paid tournaments

            if entry_fee > 0:

                if profile.xp < entry_fee:

                    return render_join_page(
                        error="You do not have enough coins."
                    )

                # Deduct coins

                profile.xp -= entry_fee

                profile.save(
                    update_fields=["xp"]
                )

            # -----------------------------------------
            # REGISTER TEAM OR PLAYER
            # -----------------------------------------

            if tournament.category == "team":

                selected_team.tournaments.add(
                    tournament
                )

            else:

                tournament.players.add(
                    request.user
                )

        # -----------------------------------------
        # SUCCESS MESSAGE ON SAME PAGE
        # -----------------------------------------

        if entry_fee > 0:

            success_message = (
                f"Paid {entry_fee} coins and successfully "
                "joined the tournament."
            )

        else:

            success_message = (
                "Successfully joined the tournament."
            )

        return render_join_page(
            success=success_message
        )

    # -----------------------------------------
    # GET REQUEST
    # -----------------------------------------

    return render_join_page()


@login_required
def friendly_match_creation(request):

    form = freindly_match_making_form(
        request.POST or None,
        request_user=request.user
    )
    

    if request.method == "POST":

        if form.is_valid():

            try:
                match = form.save(commit=False)
                match.friendly_match_room = True
                match.save()

                form.save_m2m()

                match.match_players.add(request.user)

                for player in match.match_players.all():
                    match_player.objects.create(
                        match=match,
                        user=player,
                        ready=False
                    )

                print("match created")

                return redirect("dashboard")

            except Exception as e:
                print(e)

        else:
            print(form.errors)

    return render(
        request,
        "arena/forms/friendly_match.html",
        {"form": form}
    )