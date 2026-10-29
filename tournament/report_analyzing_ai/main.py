from .game_models import e_footbll
from tournament.models import Match,Team,match_result_form
from accounts.models import user_profile
from django.contrib.auth.models import User
import json
import os
import traceback
from django.shortcuts import get_object_or_404

def match_data(match_id):
    match = Match.objects.get(id=match_id)
    result=match_result_form.objects.get(match=match)

    if match.friendly_match_room == True:
        tournament_name="none"
        tournament_id="none"
        winner_team="none"
    else:
        tournament_name=match.tournament.name
        tournament_id=match.tournament.id
        winner_team=match.winner_team


    return {
        "id": match.id,
        "name": match.name,
        "tournament_name":tournament_name,
        "tournament_id": tournament_id,
        "winner_user": match.winner_user,
        "winner_team":winner_team,
        "game": match.game,
        "image": result.screenshot.path,
        "players": match.match_players.name
    }
    


result_file = "match_result.json"

if os.path.exists(result_file):
    with open(result_file, "r") as f:
        matches = json.load(f)
else:
    matches = []
print(os.path.abspath(result_file))


def analyze_match(match_info, response_text):
    match_id=match_info["id"]
    match = Match.objects.select_related("tournament").get(id=match_id)
    if response_text.startswith("```"):
        response_text = response_text.replace("```json", "").replace( "```", "").strip()
    #print(response_text)
    try:   
        data = json.loads(response_text)
        #print("JSON Loaded:", data)
        data["tournament_id"] = match_info["tournament_id"]
        data["match_id"] = match_info["id"]
        data["match_name"] = match_info["name"]
        data["tournament_name"] = match_info["tournament_name"]
        data["game"] = match_info["game"]
        data["image"] = match_info["image"]
        #print(type(matches))
        #print(matches)
        matches.append(data)
        #print("data uploaded",data)
        winner_name=data["winner"]
        #print("winner is :",winner_name)

        if match.tournament is None:
            winner = get_object_or_404(User, username=data["winner"])
            match.winner_user = winner
            if match.loot_enable:
                players = list(match.match_players.all())
                number_of_players = len(players)
                if number_of_players > 0:
                    loot_split = match.loot // number_of_players
                    total_loot=match.loot

                    for player in players:
                        profile = player.profile
                        if profile.xp < loot_split:
                            raise ValueError(f"{player.username} does not have enough coins")
                    for player in players:
                        profile = player.profile
                        profile.xp -= loot_split
                        profile.save(update_fields=["xp"])
                    winner_profile = winner.profile
                    winner_profile.xp += total_loot
                    winner_profile.save(update_fields=["xp"])
                    #print("loot given")

        elif match.tournament.category == "team":   
            winner_team=Team.objects.filter(name=winner_name).first()
            if winner_team:
                match.winner_team=winner_team
                users = winner_team.user.all()
                for user in users:
                    player_profile= user_profile.objects.get(user=user)
                    if player_profile:
                        player_profile.xp += 50
                        player_profile.save()               
            else:
                error="failed to assign winner team becuse no team found , please check that your team name/username(if it solo tournament) is same as in game if not please request to add score by sending a mail to this email "
                print (error)
                return error
        elif match.tournament.category == "solo":
            player = get_object_or_404(User,username=data["winner"])
            match.winner_user=player

        else:
            winner = get_object_or_404(User, username=data["winner"])
            match.winner_user = winner
            if match.loot_enable:
                players = list(match.match_players.all())
                number_of_players = len(players)
                if number_of_players > 0:
                    loot_split = match.loot // number_of_players
                    total_loot=match.loot

                    for player in players:
                        profile = player.profile
                        if profile.xp < loot_split:
                            raise ValueError(f"{player.username} does not have enough coins")
                    for player in players:
                        profile = player.profile
                        profile.xp -= loot_split
                        profile.save(update_fields=["xp"])
                    winner_profile = winner.profile
                    winner_profile.xp += total_loot
                    winner_profile.save(update_fields=["xp"])

        match.save() 
           

        with open(result_file, "w") as f:
           json.dump(matches, f, indent=4)
           print("Saved to:", result_file)
    except Exception as e:
        print(f"data failed to update {e}")
        traceback.print_exc()


    return data