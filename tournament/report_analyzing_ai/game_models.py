from google import genai
import time
from PIL import Image
import os
GCP_API_KEY = os.environ.get("GCP_API_KEY")
client=genai.Client(
    api_key=GCP_API_KEY
    )

def e_footbll(image):
    print("request reached ")
    from .main import analyze_match
  
    prompt = """
    You are an OCR system.

Read ONLY the visible text in this eFootball result image.

Do NOT guess or infer any value.
If a value is not visible, return null.

The image may be either:
1. A statistics screen.
2. A final result screen.

Extract:

- left_team
- right_team
- left_score
- right_score

Winner Rules:
- Higher score wins.
- If scores are equal and a PK score is shown, use the PK score.
- Otherwise return "Draw".

Return ONLY valid JSON.

{
  "left_team": "",
  "right_team": "",
  "left_score": null,
  "right_score": null,
  "winner": ""
}
     
        """
    
    print("===== Gemini Request Started =====")
    print("Time:", time.strftime("%H:%M:%S"))
  
    if image:
        print(image)
    else :
        print("image not reached")

    request_image=Image.open(image)

    print("Request reached")

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=[request_image, prompt]
    )

    print(response.text)

    return response.text

def fc_football(image):
    print("request reached ")
    from .main import analyze_match
  
    prompt = """
You are an OCR system for EA SPORTS FC match result images.

Read ONLY the visible text in this FC match result image.

Do NOT guess, infer, or invent any value.
If a value is not clearly visible, return null.

The image may be:
1. An FC Match Results / Final Result screen.
2. An in-game final scoreboard.
3. A scoreboard showing Home and Away teams.
4. A result screen showing a penalty shootout score.

Extract ONLY the following:

- left_team
- right_team
- left_score
- right_score
- penalty_left_score
- penalty_right_score
- winner

TEAM IDENTIFICATION:
- Identify the team name associated with the LEFT side of the scoreboard.
- Identify the team name associated with the RIGHT side of the scoreboard.
- If player/user names are shown separately from the football club name, extract the FOOTBALL CLUB name as left_team/right_team.
- Do not use a player's name as the team name when a football club name is visible.
- If only a player name is visible and no football club name is visible, use the visible player name.
- Do not guess a team name from a logo if the team name is not visible.

SCORE IDENTIFICATION:
- Extract the normal/full-time score shown for the left and right teams.
- Do not confuse individual goal timestamps or player statistics with the final score.
- If the score is not clearly visible, return null.

PENALTY SHOOTOUT:
- If a penalty shootout score is explicitly shown, extract it separately.
- Examples of penalty notation include:
  (4-1P)
  (4-1 pens)
  4-1 PEN
  4-1 PK
  or another clearly visible penalty-shootout indicator.
- Do NOT treat the penalty score as the normal match score.
- If no penalty shootout score is visible, return null for both penalty fields.

WINNER RULES:

1. Compare left_score and right_score.

2. If left_score is greater than right_score:
   winner = left_team

3. If right_score is greater than left_score:
   winner = right_team

4. If the normal scores are equal:
   - Check whether a penalty shootout score is clearly visible.
   - If penalty_left_score is greater than penalty_right_score:
       winner = left_team
   - If penalty_right_score is greater than penalty_left_score:
       winner = right_team
   - If no penalty shootout winner can be determined:
       winner = "Draw"

5. Never determine the winner from:
   - possession
   - shots
   - player ratings
   - team strength
   - logos
   - commentary
   - goal timestamps
   - assumptions

IMPORTANT:
- For a score such as 4-4 (4-1P), the normal score is:
    left_score = 4
    right_score = 4
    penalty_left_score = 4
    penalty_right_score = 1

- Therefore the left team is the winner.

- If the image shows only 4-4 with no visible penalty result, return:
    winner = "Draw"

Return ONLY valid JSON.
Do not include markdown.
Do not include explanations.

{
  "left_team": null,
  "right_team": null,
  "left_score": null,
  "right_score": null,
  "penalty_left_score": null,
  "penalty_right_score": null,
  "winner": null
}
"""
     
     
    
    print("===== Gemini Request Started =====")
    print("Time:", time.strftime("%H:%M:%S"))
  
    if image:
        print(image)
    else :
        print("image not reached")

    request_image=Image.open(image)

    print("Request reached")

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=[request_image, prompt]
    )

    print(response.text)

    return response.text


def other(image):
    print("request reached ")
    from .main import analyze_match
  
    prompt = """
You are a highly accurate OCR and game-result extraction system.

Your task is to read ONLY the visible information in the provided
video-game match/result screenshot.

IMPORTANT RULES:
- Read only information that is actually visible in the image.
- Do NOT guess.
- Do NOT infer information from logos, colors, player names,
  team reputation, rankings, statistics, or previous knowledge.
- Do NOT invent missing values.
- If something is not clearly visible, return null.
- If text is partially visible or unreadable, return null.
- Do not confuse player names, team names, character names,
  usernames, statistics, scores, rankings, or timestamps.
- Do not use external knowledge to complete missing information.

The screenshot can belong to ANY competitive video game.

Examples include:
- Football / soccer games
- Battle royale games
- FPS games
- Racing games
- Fighting games
- Sports games
- MOBA games
- Strategy games
- Multiplayer games
- Team-based games
- Solo games
- Tournament result screens

The image may be:
1. A final result screen.
2. A scoreboard.
3. A post-match statistics screen.
4. A match summary.
5. A tournament result screen.
6. An end-of-game screen.
7. An in-game scoreboard showing the final result.

====================================================
STEP 1 — IDENTIFY THE GAME
====================================================

Identify the game ONLY if its name is clearly visible.

If the game name is not clearly visible:
"game": null

====================================================
STEP 2 — IDENTIFY THE PARTICIPANTS
====================================================

Extract all clearly visible competitors.

A competitor can be:
- A player
- A username
- A team
- A football club
- A basketball team
- A racing driver
- A racing team
- A fighting-game player
- A squad
- Any other game participant

Determine whether the result is:
- solo
- team
- unknown

Do NOT assume a participant is a team or player unless the image
provides enough information.

====================================================
STEP 3 — EXTRACT THE RESULT
====================================================

Extract every clearly visible result value that is relevant to
determining the match result.

Possible values include:

- score
- points
- kills
- assists
- placement
- rank
- rounds won
- rounds lost
- laps
- race position
- time
- goals
- sets
- games won
- damage
- eliminations
- objectives
- any other clearly displayed final result value

Do NOT assume that a particular statistic determines the winner.

For example:

Football:
4 - 2

Battle Royale:
1st place, 12 kills

Racing:
1st position, 02:15.421

Fighting game:
3 rounds - 1 round

FPS:
Team A 13 - Team B 9

====================================================
STEP 4 — DETERMINE THE WINNER
====================================================

Determine the winner ONLY when the image clearly establishes it.

Use the game's visible result information.

Examples:

- If a football score is 4-2, the participant with 4 wins.
- If a race clearly shows one participant in 1st place, that
  participant wins.
- If a battle royale result clearly shows 1st place, that
  participant/team wins.
- If a fighting game clearly shows one participant winning more
  rounds and the final result establishes the winner, use that.
- If the game explicitly displays "WINNER", "VICTORY", "DEFEAT",
  "1ST", "CHAMPION", or equivalent result text, use that only when
  it clearly identifies the participant.
- If a penalty/shootout/tiebreaker is clearly displayed, use the
  tiebreaker to determine the winner when appropriate.

If the result is tied and no visible tiebreaker determines a winner:

"winner": "Draw"

If the winner cannot be determined reliably:

"winner": null

NEVER guess a winner.

====================================================
STEP 5 — TIEBREAKERS
====================================================

If the normal result is tied, look for a clearly visible
tiebreaker.

Possible tiebreakers include:

- penalties / PK
- overtime
- extra time
- sudden death
- rounds
- sets
- additional points
- race position
- other explicitly displayed tiebreaker

Use a tiebreaker ONLY if it is clearly visible.

====================================================
STEP 6 — RAW VISIBLE RESULT
====================================================

Also return the important visible result information as text.

Do not create information that is not visible.

====================================================
OUTPUT FORMAT
====================================================

Return ONLY valid JSON.

Do not use Markdown.

Do not add explanations.

Use null when information is unavailable.

{
  "game": null,
  "match_type": null,

  "participants": [
    {
      "name": null,
      "type": null,
      "score": null,
      "points": null,
      "kills": null,
      "placement": null,
      "rank": null,
      "rounds_won": null,
      "rounds_lost": null,
      "position": null,
      "time": null
    }
  ],

  "winner": null,

  "result": null,

  "tiebreaker": {
    "used": false,
    "type": null,
    "left": null,
    "right": null
  }
}
    """
    
    print("===== Gemini Request Started =====")
    print("Time:", time.strftime("%H:%M:%S"))
  
    if image:
        print(image)
    else :
        print("image not reached")

    request_image=Image.open(image)

    print("Request reached")

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=[request_image, prompt]
    )

    print(response.text)

    return response.text