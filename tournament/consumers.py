import asyncio
import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from django.template.loader import render_to_string
from django.utils import timezone

from .models import Match, match_player


# ============================================================
# FIXED COUNTDOWN
# ============================================================

COUNTDOWN_SECONDS = 12


# ============================================================
# COUNTDOWN START TIMES
# ============================================================
#
# Stored only in memory.
#
# Example:
#
# {
#     35: datetime(...),
#     36: datetime(...)
# }
#
# ============================================================

countdown_times = {}


class MatchRoomConsumer(AsyncWebsocketConsumer):

    # ========================================================
    # CONNECT
    # ========================================================

    async def connect(self):

        # ----------------------------------------------------
        # GET MATCH ID
        # ----------------------------------------------------

        self.match_id = self.scope[
            "url_route"
        ]["kwargs"]["match_id"]

        self.room_group_name = (
            f"match_{self.match_id}"
        )

        self.user = self.scope["user"]

        # ----------------------------------------------------
        # CHECK LOGIN
        # ----------------------------------------------------

        if self.user.is_anonymous:

            print(
                "❌ Anonymous user tried to connect"
            )

            await self.close()
            return

        # ----------------------------------------------------
        # GET MATCH
        # ----------------------------------------------------

        match = await self.get_match()

        if not match:

            print(
                f"❌ Match {self.match_id} "
                f"does not exist"
            )

            await self.close()
            return

        # ----------------------------------------------------
        # CHECK WHETHER USER IS A PLAYER
        # ----------------------------------------------------

        is_player = await self.is_match_player()

        if not is_player:

            print(
                f"❌ {self.user.username} "
                f"is not a player in "
                f"Match {self.match_id}"
            )

            await self.close()
            return

        # ----------------------------------------------------
        # UPDATE MATCH STATE
        # ----------------------------------------------------

        state = await self.update_match_state()

        # Match has not started yet
        if state == "closed":

            print(
                f"🔒 Match {self.match_id} "
                f"is not open yet"
            )

            await self.close()
            return

        # ----------------------------------------------------
        # JOIN CHANNEL GROUP
        # ----------------------------------------------------

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        print(
            f"🟢 {self.user.username} "
            f"connected to Match "
            f"{self.match_id}"
        )

        # ----------------------------------------------------
        # START TIMER
        # ----------------------------------------------------

        self.timer_task = asyncio.create_task(
            self.match_timer()
        )

        # ----------------------------------------------------
        # SEND CURRENT MATCH STATE
        # ----------------------------------------------------

        await self.broadcast_match()

        # ----------------------------------------------------
        # SEND ONLY THIS USER'S READY BUTTON
        # ----------------------------------------------------

        await self.send_own_ready_button()

    # ========================================================
    # DISCONNECT
    # ========================================================

    async def disconnect(self, close_code):

        # ----------------------------------------------------
        # CANCEL TIMER
        # ----------------------------------------------------

        task = getattr(
            self,
            "timer_task",
            None
        )

        if task:

            task.cancel()

        # ----------------------------------------------------
        # LEAVE CHANNEL GROUP
        # ----------------------------------------------------

        if hasattr(
            self,
            "room_group_name"
        ):

            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

        print(
            f"🔴 {self.user.username} "
            f"disconnected from Match "
            f"{self.match_id}"
        )

    # ========================================================
    # RECEIVE WEBSOCKET MESSAGE
    # ========================================================

    async def receive(
        self,
        text_data
    ):

        print(
            "\n=============================="
        )

        print(
            "🔵 WEBSOCKET RECEIVE"
        )

        print(
            "=============================="
        )

        print(
            "Raw data:",
            text_data
        )

        # ----------------------------------------------------
        # PARSE JSON
        # ----------------------------------------------------

        try:

            data = json.loads(
                text_data
            )

        except json.JSONDecodeError:

            print(
                "❌ Invalid JSON"
            )

            return

        print(
            "Parsed data:",
            data
        )

        # ----------------------------------------------------
        # GET ACTION
        # ----------------------------------------------------

        action = data.get(
            "action"
        )

        print(
            "Action:",
            action
        )

        print(
            "User:",
            self.user.username
        )

        print(
            "Match ID:",
            self.match_id
        )

        # ----------------------------------------------------
        # VALIDATE ACTION
        # ----------------------------------------------------

        if action not in [
            "ready",
            "not-ready"
        ]:

            print(
                "❌ Invalid action"
            )

            return

        print(
            "✅ Valid action"
        )

        # ----------------------------------------------------
        # UPDATE READY STATE
        # ----------------------------------------------------

        result = await self.update_ready(
            action
        )

        print(
            "update_ready result:",
            result
        )

        if not result:

            print(
                "❌ Ready state "
                "was not updated"
            )

            return

        print(
            "✅ Ready state updated"
        )

        # ----------------------------------------------------
        # CHECK EVERYONE READY
        # ----------------------------------------------------

        await self.check_everyone_ready()

        print(
            "✅ Everyone-ready check completed"
        )

        # ----------------------------------------------------
        # UPDATE THIS USER'S BUTTON
        # ----------------------------------------------------

        await self.send_own_ready_button()

        # ----------------------------------------------------
        # UPDATE EVERYONE'S MATCH UI
        # ----------------------------------------------------

        await self.broadcast_match()

        print(
            "✅ Broadcast completed"
        )

        print(
            "==============================\n"
        )

    # ========================================================
    # MATCH TIMER
    # ========================================================

    async def match_timer(self):

        try:

            while True:

                # ------------------------------------------------
                # CHECK EVERY SECOND
                # ------------------------------------------------

                await asyncio.sleep(1)

                state = (
                    await self.update_match_state()
                )

                # ================================================
                # MATCH FINISHED
                # ================================================

                if state == "finished":

                    # Update match information
                    await self.broadcast_match()

                    # Remove Ready button
                    await self.send_own_ready_button()

                    # Stop this timer
                    break

                # ================================================
                # OPEN
                # COUNTDOWN
                # LIVE
                # ================================================

                if state in [
                    "open",
                    "countdown",
                    "live"
                ]:

                    # Update common match UI
                    await self.broadcast_match()

                    # Update this user's Ready button
                    await self.send_own_ready_button()

        except asyncio.CancelledError:

            print(
                f"⏹ Timer cancelled "
                f"for Match {self.match_id}"
            )

    # ========================================================
    # UPDATE MATCH STATE
    # ========================================================

    @database_sync_to_async
    def update_match_state(self):

        match = Match.objects.get(
            id=self.match_id
        )

        now = timezone.now()
       
        # ====================================================
        # SCHEDULED → OPEN
        # ====================================================

        if match.status == "scheduled":

            # ------------------------------------------------
            # MATCH START TIME REACHED
            # ------------------------------------------------

            if (
                match.match_start_time
                and now >= match.match_start_time
            ):

                match.status = "open"

                match.save(
                    update_fields=[
                        "status"
                    ]
                )

                print(
                    f"🟢 Match {match.id} "
                    f"is now OPEN"
                )

            # ------------------------------------------------
            # NOT STARTED YET
            # ------------------------------------------------

            else:

                return "scheduled"

        # ====================================================
        # COUNTDOWN
        # ====================================================

        if match.status == "countdown":

            # ------------------------------------------------
            # GET COUNTDOWN START
            # ------------------------------------------------

            countdown_start = (
                countdown_times.get(
                    match.id
                )
            )

            # ------------------------------------------------
            # SAFETY
            # ------------------------------------------------

            if countdown_start is None:

                countdown_times[
                    match.id
                ] = now

                countdown_start = now

                print(
                    f"⏳ Countdown initialized "
                    f"for Match {match.id}"
                )

            # ------------------------------------------------
            # CHECK WHETHER EVERYONE IS STILL READY
            # ------------------------------------------------

            players = (
                match.match_player.all()
            )

            total_players = (
                players.count()
            )

            ready_players = (
                players.filter(
                    ready=True
                ).count()
            )

            # ------------------------------------------------
            # SOMEONE BECAME NOT READY
            # ------------------------------------------------

            if (
                total_players == 0
                or ready_players != total_players
            ):

                match.status = "open"

                match.save(
                    update_fields=[
                        "status"
                    ]
                )

                countdown_times.pop(
                    match.id,
                    None
                )

                print(
                    f"🛑 Countdown cancelled "
                    f"for Match {match.id}"
                )

                return "open"

            # ------------------------------------------------
            # CALCULATE ELAPSED TIME
            # ------------------------------------------------

            elapsed = (
                now - countdown_start
            ).total_seconds()

            # ------------------------------------------------
            # COUNTDOWN FINISHED
            # ------------------------------------------------

            if elapsed >= COUNTDOWN_SECONDS:

                match.status = "live"

                match.started_at = now

                # --------------------------------------------
                # MATCH END TIME
                # --------------------------------------------

                match.match_end_time = (
                    now + match.duration
                )

                match.save(
                    update_fields=[
                        "status",
                        "started_at",
                        "match_end_time"
                    ]
                )

                countdown_times.pop(
                    match.id,
                    None
                )

                print(
                    f"🔥 Match {match.id} "
                    f"is now LIVE"
                )

                return "live"

            return "countdown"

        # ====================================================
        # LIVE
        # ====================================================

        if match.status == "live":

            # ------------------------------------------------
            # CHECK MATCH END TIME
            # ------------------------------------------------

            if (
                match.match_end_time
                and now >= match.match_end_time
            ):

                match.status = "finished"

                match.ended_at = now

                match.save(
                    update_fields=[
                        "status",
                        "ended_at"
                    ]
                )

                # --------------------------------------------
                # DELETE TEMPORARY MATCH PLAYERS
                # --------------------------------------------

                match.match_player.all().delete()

                # --------------------------------------------
                # REMOVE COUNTDOWN IF ANY
                # --------------------------------------------

                countdown_times.pop(
                    match.id,
                    None
                )

                print(
                    f"🏁 Match {match.id} "
                    f"FINISHED"
                )

                return "finished"

            return "live"

        # ====================================================
        # OPEN
        # ====================================================

        if match.status == "open":

            return "open"

        # ====================================================
        # FINISHED
        # ====================================================

        if match.status == "finished":

            return "finished"

        # ====================================================
        # DEFAULT
        # ====================================================

        return match.status

    # ========================================================
    # UPDATE READY STATE
    # ========================================================

    @database_sync_to_async
    def update_ready(
        self,
        action
    ):

        match = Match.objects.get(
            id=self.match_id
        )

        # ====================================================
        # ONLY OPEN / COUNTDOWN
        # ====================================================

        if match.status not in [
            "open",
            "countdown"
        ]:

            print(
                "❌ Cannot change ready status."
            )

            print(
                "Current status:",
                match.status
            )

            return False

        # ====================================================
        # FIND PLAYER
        # ====================================================

        player = (
            match.match_player
            .filter(
                user=self.user
            )
            .first()
        )

        if not player:

            print(
                "❌ match_player does not exist "
                f"for {self.user.username}"
            )

            return False

        # ====================================================
        # READY
        # ====================================================

        if action == "ready":

            player.ready = True

        # ====================================================
        # NOT READY
        # ====================================================

        elif action == "not-ready":

            player.ready = False

        # ====================================================
        # SAVE
        # ====================================================

        player.save(
            update_fields=[
                "ready"
            ]
        )

        print(
            f"✅ {self.user.username} "
            f"ready = {player.ready}"
        )

        # ====================================================
        # IMPORTANT
        # ====================================================
        #
        # If someone clicks NOT READY during countdown,
        # immediately cancel countdown.
        #
        # ====================================================

        if (
            action == "not-ready"
            and match.status == "countdown"
        ):

            match.status = "open"

            match.save(
                update_fields=[
                    "status"
                ]
            )

            countdown_times.pop(
                match.id,
                None
            )

            print(
                "🛑 COUNTDOWN CANCELLED"
            )

            print(
                "↩️ Match returned to OPEN"
            )

        return True

    # ========================================================
    # CHECK EVERYONE READY
    # ========================================================

    @database_sync_to_async
    def check_everyone_ready(self):

        match = Match.objects.get(
            id=self.match_id
        )

        # ====================================================
        # ONLY OPEN / COUNTDOWN
        # ====================================================

        if match.status not in [
            "open",
            "countdown"
        ]:

            return False

        # ====================================================
        # GET PLAYERS
        # ====================================================

        players = (
            match.match_player.all()
        )

        if not players.exists():

            print(
                "⚠️ No match players found"
            )

            return False

        # ====================================================
        # CHECK ALL READY
        # ====================================================

        player_list = list(
            players.values(
                "user__username",
                "ready"
            )
        )
        
        print("👥 MATCH PLAYERS:", player_list)
        
        all_ready = not players.filter(
            ready=False
        ).exists()
        
        print("👥 ALL READY:", all_ready)
        # ====================================================
        # EVERYONE READY
        # ====================================================

        if all_ready:

            # ------------------------------------------------
            # START COUNTDOWN
            # ------------------------------------------------

            if match.status == "open":

                match.status = "countdown"

                countdown_times[
                    match.id
                ] = timezone.now()

                match.save(
                    update_fields=[
                        "status"
                    ]
                )

                print(
                    "================================"
                )

                print(
                    "⏳ ALL PLAYERS READY"
                )

                print(
                    "⏳ 12 SECOND COUNTDOWN STARTED"
                )

                print(
                    "================================"
                )

            return True

        # ====================================================
        # SOMEONE NOT READY
        # ====================================================

        if match.status == "countdown":

            match.status = "open"

            countdown_times.pop(
                match.id,
                None
            )

            match.save(
                update_fields=[
                    "status"
                ]
            )

            print(
                "↩️ COUNTDOWN CANCELLED"
            )

        return False

    # ========================================================
    # CHECK WHETHER USER IS A MATCH PLAYER
    # ========================================================

    @database_sync_to_async
    def is_match_player(self):
        match = (
            Match.objects
            .select_related("tournament")
            .filter(id=self.match_id)
            .first()
        )
    
        if not match:
            return False
    
        # Friendly match: participants are match_player records.
        if match.friendly_match_room:
            return match.match_player.filter(
                user=self.user
            ).exists()
    
        # Tournament match must have a tournament.
        if not match.tournament:
            return False
    
        # Team tournament.
        if match.tournament.category == "team":
            return match.teams.filter(
                user=self.user
            ).exists()
    
        # Solo tournament.
        if match.tournament.category == "solo":
            return match.match_players.filter(
                id=self.user.id
            ).exists()
    
        return False

    # ========================================================
    # GET CURRENT USER'S MATCH PLAYER
    # ========================================================

    @database_sync_to_async
    def get_player(self):

        return (
            match_player.objects
            .filter(
                match_id=self.match_id,
                user=self.user
            )
            .first()
        )

    # ========================================================
    # GET MATCH
    # ========================================================

    @database_sync_to_async
    def get_match(self):

        return (
            Match.objects
            .select_related(
                "tournament"
            )
            .filter(
                id=self.match_id
            )
            .first()
        )

    # ========================================================
    # SEND ONLY THIS USER'S READY BUTTON
    # ========================================================

    async def send_own_ready_button(self):

        player = await self.get_player()

        match = await self.get_match()

        if not match:

            return

        # ====================================================
        # UNIQUE CONTAINER FOR THIS USER
        # ====================================================

        container_id = (
            f"ready-container-{self.user.id}"
        )

        # ====================================================
        # LIVE / FINISHED
        # REMOVE BUTTON
        # ====================================================

        if match.status in [
            "live",
            "finished"
        ]:

            html = f"""
            <div
                id="{container_id}"
                hx-swap-oob="innerHTML"
            >
            </div>
            """

        # ====================================================
        # OPEN / COUNTDOWN
        # ====================================================

        elif (
            match.status in [
                "open",
                "countdown"
            ]
            and player
        ):

            # ------------------------------------------------
            # USER IS READY
            # ------------------------------------------------

            if player.ready:

                action = "not-ready"

                button_text = "Not Ready"

                button_class = (
                    "btn btn-danger"
                )

            # ------------------------------------------------
            # USER IS NOT READY
            # ------------------------------------------------

            else:

                action = "ready"

                button_text = "Ready"

                button_class = (
                    "btn btn-success"
                )

            # ------------------------------------------------
            # BUILD BUTTON HTML
            # ------------------------------------------------

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

        # ====================================================
        # SEND RAW HTML
        # ====================================================
        #
        # IMPORTANT:
        #
        # DO NOT json.dumps() this.
        #
        # HTMX websocket extension expects the HTML directly.
        #
        # ====================================================

        await self.send(
            text_data=html
        )

    # ========================================================
    # BROADCAST MATCH
    # ========================================================

    async def broadcast_match(self):

        html = (
            await self.render_match_html()
        )

        await self.channel_layer.group_send(

            self.room_group_name,

            {
                "type": "match_update",

                "html": html,
            }

        )

    # ========================================================
    # RECEIVE BROADCAST
    # ========================================================

    async def match_update(
        self,
        event
    ):

        await self.send(
            text_data=event["html"]
        )

    # ========================================================
    # RENDER MATCH HTML
    # ========================================================

    @database_sync_to_async
    def render_match_html(self):
        match = (
            Match.objects
            .select_related("tournament")
            .prefetch_related(
                "teams__user",
                "match_players",
                "match_player__user",
            )
            .filter(id=self.match_id)
            .first()
        )
    
        if not match:
            return ""
    
        team_data = []
        solo_players = []
    
        # --------------------------------------------------------
        # FRIENDLY MATCH
        # --------------------------------------------------------
        # Friendly matches use match_player records and may not
        # have a tournament attached.
        # --------------------------------------------------------
    
        if match.friendly_match_room:
            for player_record in match.match_player.select_related(
                "user"
            ).all():
                solo_players.append({
                    "user": player_record.user,
                    "match_player": player_record,
                })
    
        # --------------------------------------------------------
        # TOURNAMENT MATCH
        # --------------------------------------------------------
    
        elif match.tournament:
    
            # ----------------------------------------------------
            # TEAM TOURNAMENT
            # ----------------------------------------------------
    
            if match.tournament.category == "team":
                for team in match.teams.prefetch_related("user").all():
                    team_players = []
    
                    for user in team.user.all():
                        player_record = (
                            match.match_player
                            .filter(user=user)
                            .first()
                        )
    
                        team_players.append({
                            "user": user,
                            "match_player": player_record,
                        })
    
                    team_data.append({
                        "team": team,
                        "players": team_players,
                    })
    
            # ----------------------------------------------------
            # SOLO TOURNAMENT
            # ----------------------------------------------------
    
            elif match.tournament.category == "solo":
                player_records = {
                    record.user_id: record
                    for record in match.match_player.select_related(
                        "user"
                    ).all()
                }
    
                for user in match.match_players.all():
                    solo_players.append({
                        "user": user,
                        "match_player": player_records.get(user.id),
                    })
    
        # --------------------------------------------------------
        # RENDER PLAYER PARTIAL
        # --------------------------------------------------------
    
        teams_html = render_to_string(
            "tournament/partials/match_players.html",
            {
                "team_data": team_data,
                "solo_players": solo_players,
                "match": match,
                "is_friendly": match.friendly_match_room,
            },
        )
    
        # --------------------------------------------------------
        # STATUS
        # --------------------------------------------------------
    
        status_html = f"""
        <div id="match-status" hx-swap-oob="innerHTML">
            {match.status.upper()}
        </div>
        """
    
        # --------------------------------------------------------
        # TIMER
        # --------------------------------------------------------
    
        if match.status == "countdown":
            countdown_start = countdown_times.get(match.id)
    
            if countdown_start:
                elapsed = (
                    timezone.now() - countdown_start
                ).total_seconds()
    
                remaining = max(
                    0,
                    COUNTDOWN_SECONDS - int(elapsed)
                )
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
    
     