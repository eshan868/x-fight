# X-Fight - The GameArena

## You can explore this website on : https://x-fight-two.vercel.app/

<img width="1338" height="608" alt="image" src="https://github.com/user-attachments/assets/d0662248-2506-4884-bb9a-3a5f7162d21f" />

This is a gaming community and tournament managing website built using Python and Django. It is developed for gamers who want everything in one platform.
like other website this website can host tournaments, host friendly matches, chat with other gamers, and call them and dominate by having high stats

## why I created this?
I know that there are websites like slack, discord and in almost all the games has tournament system and leaderboard but that is for that game, but I want the gamers that dominate whole the gamming community that's where this X-fight comes and that's why I created it 

## Working of X-Fight
in this x-fight there some features in that the main features are.

### The Main Features

- GameMate system for connecting with other players.
- Tournament creation and management.
- Friendly match creation and participation.
- One-to-one and group chat functionality.
- Team management and team meetings.
- In-platform coin and Stats.
- Match report uploads and AI-assisted match result processing.



## After Entering The Arena

### Dashboard

<img width="1334" height="646" alt="image" src="https://github.com/user-attachments/assets/cc7796d1-3aa9-4e13-869d-350c82d7cb36" />

Here the dashboard acts as the main entry point to the Site. It provides access to player-related activities and community interactions.

Players can navigate between the available sections to manage their profiles, connect with other gamers, and participate in gaming activities.

### Player Profile

In order to create an account the user must enter these much information

- Full name.
- username
- password
- Unique gamer tag.
- Profile picture.
- Age.
- Biography.
- Social medias links.
- email

The profile helps other players identify and connect with them within the gaming community. And when it comes to the profile there will be two more things that is stats and coins initial when registering the stats and the coins and the stats will be zero

### GameMates

The GameMate feature allows players to connect with other gamers. In this the Players can discover gaming partners GameMates 
When a user sends a GameMate Request to another user in notification Pannel of the receiver user an option will be seen accept or reject as their name their functionality is same to accept and reject the game mate requests  

### Discover Players
This a popup screen where all the users of the x-fight are listed from here they can send gameMate request 

## Tournaments
This is the place all the active tournaments is listed <img width="1358" height="636" alt="image" src="https://github.com/user-attachments/assets/6a4e6a00-9963-46ba-b251-bef7e1627c63" />

in this when they click the view details  there the details of the tournament will be displayed<img width="1358" height="636" alt="image" src="https://github.com/user-attachments/assets/2c4784e2-dc0e-4c83-a61c-03bcc75d94aa" />
here they can join the tournament with two possibilities 
- Team if it is Team tournament then they can select the team and register
- solo if is solo tournament then they can just join

if there is fee for the tournament then they need to pay is and then only join the fee will be coins 

### Tournament Creation

in every players dashboard there will be option to organize a tournament and in that they can select in that select there may not have a checkbox then just click gamemates names of the admins  they can create the tournament with these details 

- Tournament name
- Solo or team-based participation.
- Entry fee if it is free then it will be zero.
- tourtnament description
- tournament dates and details
- tournament admins
- reward coins


### tournament dashboard 

in here all the users can see 
- leaderboard
- scheduled matches they can enter in which their team or name is registered
- all the participating tournaments and players
<img width="1358" height="636" alt="image" src="https://github.com/user-attachments/assets/6837bca6-994e-4c49-8716-683796991a3c" />


## tournament settings dashboard 

this page can access only by the tournament admins they can do the following things 
-  leaderboard
- schedule matches
- all the participating tournaments and players
- add admins

<img width="1358" height="636" alt="image" src="https://github.com/user-attachments/assets/4c5da994-d7b3-4ff1-a9bb-84eee59e8faf" />

## Team dashboard
every players can create team with his gammemates then they can acesses this page in this page they can use the following features 
- overview
- upcomming matches for that team
- initially the team captain will be who created the team later all the team members can decide the team captain by voting in which members got majority vote    will be the team captain
- team meeting - the team meeting can be scheduled by the team memebers can join in time
- team chat - when a team ius create the team chat is automatically created and they can chat there

  <img width="1358" height="636" alt="image" src="https://github.com/user-attachments/assets/30ca2e03-3cf9-44b1-a74f-a6e91df7a597" />

## match room

when the players enter a Matchroom in left they will be seeing all the participants of that tournament and in right side thay will have the button for ready or not

if everybody in the match presses the ready and the 12 sec countdown will starts before the match duration starts and if anyone press not ready on the countdown period the countdown will rest and starts again and after countdown the button will disappear 

### Match Reports and AI-Assisted Results

This x-fight has a functionality for uploadin2g match reports and processing match results.

if it is a friendly match or solo a random player will be randomly selected to upload the screen shot of the game scoreboard 
> [!IMPORTANT]
> Set username of the x-fight and the username of game should be equal otherwise it won't publish result and reward will not given 
Depending on the configured game , the system can use AI-assisted image or result processing to extract match information.

Processed results can include:

- Left-side and right-side teams or players.
- Scores.
- Match winner.
- Draw or penalty-related outcomes, where supported.


## Friendly Matches

In addition to tournament matches, it supports the creation of friendly matches.Friendly matches allow players to organize games without creating a full tournament.
it can create between the gamemates only 

### Friendly Match Features

- Create a friendly match room.
- Select the supported game.
- Configure the match duration.
- Invite or select GameMates.
- Access the match room.
- loot

in this loot means the total amount of the coins that the winner should recive
this loot amount will be taken from every player participating in here 
the way of calculating the loot to collect is 
                        total amount /total palyers
this amount will be taken from all the participalnts 

## Chat and Real-Time Communication
in this website the players can communicate with each other with calling or chat way the tech i used here for this is Django channels and WebSocket's for real time communication

### Group Chat

The platform  support for group communication, allowing multiple players to interact within a shared chat room.

In these there are two options
-group detail: in which the details of the group will be mentioned, and the admins can change that Eg- change admin removing user ect ..
-Invite they can send invitation to the game mates through their single chat if they click join they will be joined 
-Group voice call 
-group video call
<img width="1358" height="636" alt="image" src="https://github.com/user-attachments/assets/c52119b7-a867-49ca-ab17-a8501bd974ad" />

## group detail
here all the details of the group are displayed they are 
-group name
-group admins 
-group members 
- for group admins they can remove or make a member as admin
  <img width="1358" height="636" alt="image" src="https://github.com/user-attachments/assets/2ab7c7e0-6798-4842-8061-061e31a19505" />


### one to one chat 

this is nothing othere that chating with the gamemates it has two options 
-voice call
-video call
<img width="1358" height="636" alt="image" src="https://github.com/user-attachments/assets/09ca32a9-c1c0-437c-ad1d-086889e12074" />


## Teams and Meetings

X-Fight includes team-related functionality for organizing gaming groups and coordinating activities.

### Team Management

Team features can help players organize their gaming activities and coordinate with other members.

The captain of the Team will be able manage the team 


### Voice and Video Calls Tech Stack used
<img width="1347" height="619" alt="image" src="https://github.com/user-attachments/assets/67941132-d463-4a0b-a7ba-ce071a76ed59" />

The project includes integration work for ZEGOCLOUD-based real-time communication.
The communication flow is designed to use backend-generated authentication tokens instead of exposing server-side secrets to the browser.
For the Voice and Vedio calls We have used ZEECLOUD SDK over UI KIT to give our own UI

## Coins 
 These coins can be earned by winning matches and can share is to game mates by through the page call share credits 
 and it has another page for keeping all the records for sharing the credits 
 <img width="1358" height="636" alt="image" src="https://github.com/user-attachments/assets/e8fd29fa-242f-4f46-81e4-c0934dbb7307" />
 <img width="1358" height="636" alt="image" src="https://github.com/user-attachments/assets/f97e0185-5c7e-4f00-86f5-ee964521562f" />

### Stats

All The Players can have a Stats in their Profile 
In the leaderboard who has more Stats will on top of the  position

stats buying option comes with three option 
-Starter pack
-Pro pack
-Elite pack

<img width="1358" height="636" alt="image" src="https://github.com/user-attachments/assets/dfc8a91b-afd7-45d9-aa5b-80a62d940133" />



## Technology Stack

X-Fight is built using the following technologies:

- **Python** — Core programming language.
- **Django** — Backend framework, routing, authentication, models, and application logic.
- **HTML5** — Page structure.
- **CSS3** — Styling and interface design.
- **JavaScript** — Client-side interactions and dynamic interface behavior.
- **Django Channels** — Real-time application features.
- **WebSockets** — Real-time communication.
- **Daphne** — ASGI server.
- **SQLite or PostgreSQL** — Database, depending on the configured environment.
- **ZEGOCLOUD** — Real-time communication integration.
- **AI** — Match report processing, depending on the configured provider(via google gemini)
  
The exact dependencies and services are defined by the project's current configuration and `requirements.txt`.

## Instructions to Build and Run Locally

Follow these steps to run X-Fight on your local machine.

### 1. Clone the repository

```bash
git clone https://github.com/eshan868/x-fight.git
```

### 2. Move into the project directory

```bash
cd x-fight
```

If the Django project is nested inside another directory, move into the directory containing `manage.py`.

### 3. Create a Python virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

**Windows:**

```bash
venv\Scripts\activate
```

**macOS / Linux:**

```bash
source venv/bin/activate
```

### 5. Install the required dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure environment variables

Create a `.env` file 

Add the necessary environment variables for the database, authentication providers, communication services, AI API, cloudinary and Django settings.

Add other variables only as required by the project's settings (which you can see in the settings.py which are the env varaiables is neede)


### 7. Run database migrations

```bash
python manage.py migrate
```

### 9. Start the development server

```bash
python manage.py runserver
```

### 10. Open the website

Visit the following address in your browser:

http://127.0.0.1:8000/

The website should now be available locally, provided the required settings, dependencies, and database configuration are in place.
> [!NOTE]
> THEN TEST THE FEATURE MENTIONED BELOW


## Project Structure

The project is organized into Django applications, with each application responsible for a specific part of the platform.
They are:

- **accounts** — User accounts, authentication, and player profiles.
- **discovery** — Player discovery and related community functionality.
- **social** — GameMates, chat, teams, meetings, and social interactions.
- **tournament** — Tournament management, match creation, participation, and match results.
- **Project configuration** — Django settings, URL routing, ASGI configuration, and application initialization.

## Future Improvements

- Expanded competitive tournament formats.
- More supported games and match types.
- Improved AI-assisted match result verification.
- Enhanced player statistics and leaderboards.
- Additional team and community features.
- Improved real-time notifications.
- More detailed tournament analytics.
- Further optimization for mobile devices.
- Expanded deployment support for persistent WebSocket connections and background tasks.

## Contributing

Contributions, suggestions, and bug reports are welcome.

To contribute:

1. Fork the repository.
2. Create a feature branch.
3. Implement and test your changes.
4. Commit your changes with a descriptive message.
5. Submit a pull request.

## License

This project is licensed under the [PolyForm Noncommercial License 1.0.0](https://github.com/eshan868/x-fight/blob/master/LICENSE).
Free for personal, educational and other non-commercial use. Commercial use requires my permission.

Copyright © 2026 Muhammed Eshan P

See the [LICENSE](LICENSE) file for the complete license.

The Zego SDK in `static/zego-sdk` belongs to ZEGOCLOUD and is subject to its own terms. By contributing, you agree your contributions are licensed under the same terms.
