import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.template.loader import render_to_string
from django.utils import timezone
from .models import Match, match_player

COUNTDOWN_SECONDS = 12
countdown_times = {}
class MatchRoomConsumer(AsyncWebsocketConsumer):


    async def connect(self):

        self.match_id = self.scope["url_route"]["kwargs"]["match_id"]
        self.room_group_name = (f"match_{self.match_id}")
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            #print(" unknown user tried to connect")
            await self.close()
            return

        match = await self.get_match()
        if not match:

            #print(f" Match {self.match_id} does not exist")

            await self.close()
            return

        is_player = await self.is_match_player()

        if not is_player:
            #print(f"{self.user.username} is not a player in Match {self.match_id}")
            await self.close()
            return
        state = await self.update_match_state()
        if state == "closed":
            #print(f" Match {self.match_id} is not open yet")
            await self.close()
            return
        await self.channel_layer.group_add(self.room_group_name,self.channel_name)
        await self.accept()

        #print(f" {self.user.username} connected to Match {self.match_id}")

        self.timer_task = asyncio.create_task(self.match_timer())

        await self.broadcast_match()
        await self.send_own_ready_button()



    async def disconnect(self, close_code):
        task = getattr(self,"timer_task",None)
        if task:
            task.cancel()


        if hasattr(self,"room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

        #print(f" {self.user.username} disconnected from Match {self.match_id}")

 

    async def receive(self,text_data):

        #print(" WEBSOCKET RECEIVE")
        #print("Raw data:",text_data)

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:

            #print(" Invalid JSON")
            return

        #print("Parsed data:", data)

        action = data.get("action")
        #print("Action:",action)
        #print("User:",self.user.username)
        #print("Match ID:",self.match_id)

        if action not in ["ready","not-ready"]:
            #print(" Invalid action")
            return
        #print("Valid action")

        result = await self.update_ready(action)

       #print("update_ready result:",result)
        if not result:
            #print("Ready state ""was not updated")
            return
        #print("Ready state updated")

        await self.check_everyone_ready()
        #print(" Everyone-ready check completed")
        await self.send_own_ready_button()
        await self.broadcast_match()

        #print("Broadcast completed")

    async def match_timer(self):
        try:
            while True:

                await asyncio.sleep(1)
                state = (await self.update_match_state())
                if state == "finished":

                    await self.broadcast_match()
                    await self.send_own_ready_button()
                    break
                if state in ["open","countdown","live"]:
                    await self.broadcast_match()
                    await self.send_own_ready_button()

        except asyncio.CancelledError:
            print(f"Timer cancelled for Match {self.match_id}")

    @database_sync_to_async
    def update_match_state(self):
        match = Match.objects.get(id=self.match_id)
        now = timezone.now()
        if match.status == "scheduled":

            if (match.match_start_time and now >= match.match_start_time):
                match.status = "open"
                match.save(update_fields=["status"])

               # print(f" Match {match.id} is now OPEN")

            else:
                return "scheduled"


        if match.status == "countdown":
            countdown_start = (countdown_times.get(match.id))

            if countdown_start is None:
                countdown_times[match.id] = now
                countdown_start = now
                #print(f"⏳ Countdown initialized "f"for Match {match.id}")
            players = (match.match_player.all())
            total_players = (players.count())
            ready_players = (players.filter(ready=True).count())


            if (total_players == 0 or ready_players != total_players):
                match.status = "open"
                match.save(update_fields=["status"])
                countdown_times.pop(match.id,None)
                #print(f" Countdown cancelled for Match {match.id}")
                return "open"

            elapsed = (now - countdown_start).total_seconds()
            if elapsed >= COUNTDOWN_SECONDS:
                match.status = "live"
                match.started_at = now
                match.match_end_time = (now + match.duration)
                match.save(update_fields=[
                        "status",
                        "started_at",
                        "match_end_time"])
                countdown_times.pop(match.id,None)

                print(f"Match {match.id} is now LIVE")
                return "live"
            return "countdown"

        if match.status == "live":

            if (match.match_end_time and now >= match.match_end_time):
                match.status = "finished"
                match.ended_at = now
                match.save(update_fields=[
                        "status",
                        "ended_at"])
                match.match_player.all().delete()
                countdown_times.pop(match.id,None)
                print(f" Match {match.id} FINISHED")
                return "finished"
            return "live"

        if match.status == "open":
            return "open"
        if match.status == "finished":
            return "finished"
        return match.status
    
    @database_sync_to_async
    def update_ready(self,action):

        match = Match.objects.get(id=self.match_id)
        if match.status not in ["open","countdown"]:
            return False


        player = (match.match_player.filter(user=self.user).first() )
        if not player:
            return False

        if action == "ready":
            player.ready = True

        elif action == "not-ready":
            player.ready = False
        player.save(update_fields=["ready"])

 
        if (action == "not-ready"and match.status == "countdown"):
            match.status = "open"
            match.save(update_fields=["status"])
            countdown_times.pop(match.id,None)

        return True

    @database_sync_to_async
    def check_everyone_ready(self):

        match = Match.objects.get(id=self.match_id)
        if match.status not in ["open","countdown"]:
            return False
        players = ( match.match_player.all())
        if not players.exists():
            return False

        #player_list = list(players.values("user__username","ready"))
        all_ready = not players.filter(ready=False).exists()
        if all_ready:
            if match.status == "open":
                match.status = "countdown"
                countdown_times[match.id] = timezone.now()
                match.save(update_fields=["status"])
            return True

        if match.status == "countdown":
            match.status = "open"
            countdown_times.pop(match.id,None)
            match.save(update_fields=["status"])
        return False

    @database_sync_to_async
    def is_match_player(self):
        match = (Match.objects.select_related("tournament").filter(id=self.match_id).first())
        if not match:
            return False
        
        if match.friendly_match_room:
            return match.match_player.filter(user=self.user).exists()

        if not match.tournament:
            return False
   
        if match.tournament.category == "team":
            return match.teams.filter(user=self.user).exists()

        if match.tournament.category == "solo":
            return match.match_players.filter(id=self.user.id).exists()
    
        return False

    @database_sync_to_async
    def get_player(self):

        return ( match_player.objects.filter(match_id=self.match_id,user=self.user).first())
    @database_sync_to_async
    def get_match(self):
        return (Match.objects.select_related("tournament").filter(id=self.match_id).first())

    async def send_own_ready_button(self):
        player = await self.get_player()
        match = await self.get_match()
        if not match:
            return

        container_id = (f"ready-container-{self.user.id}")
        if match.status in ["live","finished"]:
            html = f"""
            <div
                id="{container_id}"
                hx-swap-oob="innerHTML"
            >
            </div>
            """

        elif (
            match.status in ["open","countdown"]and player):

            if player.ready:
                action = "not-ready"
                button_text = "Not Ready"
                button_class = ("btn btn-danger")


            else:
                action = "ready"
                button_text = "Ready"
                button_class = ("btn btn-success")

            html = f"""
            <div
                id="{container_id}"
                hx-swap-oob="innerHTML"
            >

                <form ws-send>

                    <input
                        type="hidden"
                        name="action"
                        value="{action}"
                    >

                    <button
                        type="submit"
                        class="{button_class}"
                    >
                        {button_text}
                    </button>

                </form>

            </div>
            """

        else:

            return

     
        await self.send( text_data=html)

    async def broadcast_match(self):
        html = (await self.render_match_html())
        await self.channel_layer.group_send(
            self.room_group_name,{
                "type": "match_update",
                "html": html,
            })
    async def match_update(self,event):
        await self.send(text_data=event["html"])

    @database_sync_to_async
    def render_match_html(self):
        match = (Match.objects.select_related("tournament").prefetch_related(
                "teams__user",
                "match_players",
                "match_player__user").filter(id=self.match_id).first())
    
        if not match:
            return ""
    
        team_data = []
        solo_players = []
    
        if match.friendly_match_room:
            for player_record in match.match_player.select_related("user").all():
                solo_players.append({"user": player_record.user,"match_player": player_record})
    
        elif match.tournament:
            if match.tournament.category == "team":
                for team in match.teams.prefetch_related("user").all():
                    team_players = []
                    for user in team.user.all():
                        player_record = (match.match_player.filter(user=user).first())
                        team_players.append({
                            "user": user,
                            "match_player": player_record})
                    team_data.append({
                        "team": team,
                        "players": team_players
                    })
    
            elif match.tournament.category == "solo":
                player_records = {record.user_id: record for record in match.match_player.select_related("user").all()}
                for user in match.match_players.all():
                    solo_players.append({
                        "user": user,
                        "match_player": player_records.get(user.id)
                    })
    
        teams_html = render_to_string(
            "tournament/partials/match_players.html",
            {
                "team_data": team_data,
                "solo_players": solo_players,
                "match": match,
                "is_friendly": match.friendly_match_room
            })
        status_html = f"""
        <div id="match-status" hx-swap-oob="innerHTML">
            {match.status.upper()}
        </div>
        """
    
        if match.status == "countdown":
            countdown_start = countdown_times.get(match.id)
            if countdown_start:
                elapsed = ( timezone.now() - countdown_start).total_seconds()
                remaining = max(0,COUNTDOWN_SECONDS - int(elapsed))
            else:
                remaining = COUNTDOWN_SECONDS
    
            timer_html = f"""
            <div id="timer" hx-swap-oob="innerHTML">
                {remaining}
            </div>
            """
    
        elif match.status == "live":
            timer_html = """
            <div id="timer" hx-swap-oob="innerHTML">
                LIVE
            </div>
            """
        else:
            timer_html = """
            <div id="timer" hx-swap-oob="innerHTML">
                00:00
            </div>
            """
    
        return f"""
        <div id="teams-container" hx-swap-oob="innerHTML">
            {teams_html}
        </div>
        {status_html}
        {timer_html}
        """
    
     