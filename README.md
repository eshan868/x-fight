# X-Fight — GameArena

## You can explore this website on : https://x-fight-two.vercel.app/

<img width="1338" height="608" alt="image" src="https://github.com/user-attachments/assets/d0662248-2506-4884-bb9a-3a5f7162d21f" />

**X-Fight** is a gaming community and tournament management platform built using Python and Django. It is designed for gamers who want to connect with other players, participate in tournaments, organize friendly matches, communicate with teammates, and compete in a gaming community.

Unlike a traditional gaming website, X-Fight brings multiple gaming community features together in one platform. It supports different types of matches, player connections, tournament management, in-platform communication, and an experience system.

This is one of my projects developed while learning and working with Python, Django, and modern web technologies. The goal is to create a platform where gamers can connect, compete, and manage their gaming activities in one place.

## Working of X-Fight

The features available on the website depend on the user's account, permissions, and participation in tournaments, matches, and teams.

### Main Features

- User registration and authentication.
- Player profiles with gamer tags, profile pictures, biographies, and social links.
- Gaming community and player discovery.
- GameMate system for connecting with other players.
- Tournament creation and management.
- Friendly match creation and participation.
- Match rooms with player readiness and match status management.
- Real-time communication using Django Channels and WebSockets.
- One-to-one and group chat functionality.
- Team management and team meetings.
- In-platform coin and Stats.
- Match report uploads and AI-assisted match result processing.
- Responsive gaming dashboard and player interface.

## If You Are a Player

After logging in, players can access their gaming dashboard and the features available to their account.

### Dashboard

<img width="1334" height="646" alt="image" src="https://github.com/user-attachments/assets/cc7796d1-3aa9-4e13-869d-350c82d7cb36" />

The dashboard acts as the main entry point to the gaming platform. It provides access to player-related activities, gaming features, and community interactions.

Players can navigate between the available sections to manage their profiles, connect with other gamers, and participate in gaming activities.

### Player Profile

Each player can maintain a gaming profile containing details such as:

- Full name.
- Unique gamer tag.
- Profile picture.
- Age.
- Biography.
- Social media links.
- Coins
- Stats

The profile helps other players identify and connect with them within the gaming community.

### GameMates

The GameMate feature allows players to connect with other gamers.

Players can discover potential gaming partners, send or manage connection requests, and connect with accepted GameMates.

Depending on the available features and permissions, accepted GameMates can interact through the platform's communication and friendly-match systems.

### Discover Players

Players can explore the gaming community and discover other users.

This feature helps gamers find potential teammates and expand their gaming network.

## Tournaments

X-Fight includes tournament management functionality that allows tournament organizers to manage competitive gaming events.

### Tournament Creation

Tournament organizers can configure tournament details, including:

- Tournament name and information.
- Game category.
- Solo or team-based participation.
- Entry fee, where applicable.
- Team registration limits.
- Match duration.
- Match report submission settings.
- reward coins

The available configuration depends on the tournament creation form and its validation rules.

### Tournament Participation

Players can participate in tournaments according to the configured rules.

The tournament system supports features such as:

- Tournament registration.
- Team and player participation.
- Match assignment.
- Player readiness.
- Match scheduling and status tracking.
- Match report submission.

### Match Management

Tournament matches can move through different states as they progress.
Typical match states include:

- Scheduled.
- Open.
- Countdown.
- Live.
- Finished.

The system uses match status and timing information to manage the match lifecycle.

### Ready System and Countdown

Players can mark themselves as ready before a match begins.

A countdown can be used before the match starts, helping participants prepare for the game. Match readiness and participation restrictions are handled according to the match rules.

### Match Reports and AI-Assisted Results

X-Fight includes functionality for uploading match reports and processing match results.

if it is a friendly match or solo a random player will be selected to upload the screen shot of the game scoreboard 
> [!IMPORTANT]
> Set username of the x-fight and the username of game should be equal otherwise it won't publish result and reward will not given 
Depending on the configured game and report-processing workflow, the system can use AI-assisted image or result processing to extract match information.

Processed results can include:

- Left-side and right-side teams or players.
- Scores.
- Match winner.
- Draw or penalty-related outcomes, where supported.

Match result processing and Coin rewards depend on the configured implementation.

## Friendly Matches

In addition to tournament matches, X-Fight supports the creation of friendly matches.
Friendly matches allow players to organize games without creating a full tournament.
it can create between the game mates only 

### Friendly Match Features

- Create a friendly match room.
- Select the supported game.
- Configure the match duration.
- Invite or select GameMates.
- Manage player participation.
- Allow players to mark themselves as ready.
- Access the match room.

Supported game choices depend on the current implementation and may include eFootball, EA SPORTS FC, and other games.

Available durations depend on the configured match creation form.

Friendly matches use a separate workflow from tournament matches, allowing the platform to handle casual games independently.

## Chat and Real-Time Communication

X-Fight uses Django Channels and WebSockets to support real-time features.
it also includes option for forwarding deleting the message 
deleting message has two options delete for me or delete for everyone 

### One-to-One Chat
<img width="1349" height="630" alt="image" src="https://github.com/user-attachments/assets/41d7c17e-e9e9-45d2-85fd-79f0cc7ca617" />

Players can communicate with eligible GameMates through individual chat rooms.

### Group Chat

The platform includes support for group communication, allowing multiple participants to interact within a shared chat room.

In these there are two options
-group detail: in which the details of the group will be mentioned, and the admins can change that Eg- change admin removing user ect ..
-Invite they can send invitation to the game mates through their single chat if they click join they will be joined 

### Real-Time Updates

WebSocket connections can be used to exchange messages and updates without repeatedly refreshing the page.
The exact availability of each communication feature depends on the user's permissions and the current room configuration.

In this chat room there have button for video call and voice call 

## Teams and Meetings

X-Fight includes team-related functionality for organizing gaming groups and coordinating activities.

### Team Management

Team features can help players organize their gaming activities and coordinate with other members.

The captain of the Team will be able manage the team 

### Team Meetings

The team meeting functionality provides a place for  team members to access scheduled meetings.

Depending on the configured permissions, team captains  can schedule meetings, while other members can access their meeting information and join in the time 

### Team chat 

whenever a team is created a team chat is also created in the name of that team 

This is the place where the team members can chat 

### Voice and Video Communication
<img width="1347" height="619" alt="image" src="https://github.com/user-attachments/assets/67941132-d463-4a0b-a7ba-ce071a76ed59" />

The project includes integration work for ZEGOCLOUD-based real-time communication.

The communication flow is designed to use backend-generated authentication tokens instead of exposing server-side secrets to the browser.

For the Voice and Vedio calls We have used ZEECLOUD SDK over UI KIT to give our own UI

## Coins and Experience Points

X-Fight includes a system for managing player Stats and platform-related coin balances.

### Stats

Players have a Stats in their Profile 

In the leaderboard who has more Stats will on to postion

Here winning the match the user will get coins. using that coins they can buy stats 

stats comes with three option 
-Starter pack
-Pro pack
-Elite pack

### Coin Transfers

The platform includes functionality for transferring supported coin balances between GameMates.
Transaction records can be used to track transfers and display transaction history.
All balance changes should be validated on the backend to prevent unauthorized modifications.

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
- **Google authentication** — External authentication integration, where configured.
- **AI and OCR services** — Match report processing, depending on the configured provider.
- **Git and GitHub** — Version control and source-code hosting.
- **Vercel** — Deployment, subject to ASGI, WebSocket, database, and background-processing requirements.

The exact dependencies and services are defined by the project's current configuration and `requirements.txt`.

## Instructions to Build and Run Locally

Follow these steps to run X-Fight on your local machine.

### 1. Clone the repository

Replace the repository URL with your X-Fight GitHub repository URL.

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

Add the necessary environment variables for the database, authentication providers, communication services, AI integrations, cloudinary and Django settings.

For example:

```env
SECRET_KEY=your_django_secret_key
DEBUG=True
```

Add other variables only as required by the project's settings.


### 7. Run database migrations

```bash
python manage.py migrate
```

### 8. Create an administrator account (optional)

```bash
python manage.py createsuperuser
```

Follow the prompts to create the account.

### 9. Start the development server

```bash
python manage.py runserver
```

For development involving Django Channels and WebSocket functionality, use the ASGI server and configuration appropriate to the project when required.

### 10. Open the website

Visit the following address in your browser:

http://127.0.0.1:8000/

The website should now be available locally, provided the required settings, dependencies, and database configuration are in place.

## Project Structure

The project is organized into Django applications, with each application responsible for a specific part of the platform.

The exact structure may vary depending on the current repository version.

Typical application responsibilities include:

- **accounts** — User accounts, authentication, and player profiles.
- **discovery** — Player discovery and related community functionality.
- **social** — GameMates, chat, teams, meetings, and social interactions.
- **tournament** — Tournament management, match creation, participation, and match results.
- **Project configuration** — Django settings, URL routing, ASGI configuration, and application initialization.

## Security Notes

- Set `DEBUG=False` in production and configure `ALLOWED_HOSTS` appropriately.
- Configure secure cookies, CSRF protection, and authentication settings for the production environment.


## Future Improvements

Potential areas for further development include:

- Expanded competitive tournament formats.
- More supported games and match types.
- Improved AI-assisted match result verification.
- Enhanced player statistics and leaderboards.
- Additional team and community features.
- Improved real-time notifications.
- More detailed tournament analytics.
- Further optimization for mobile devices.
- Expanded deployment support for persistent WebSocket connections and background tasks.

These improvements depend on future development and should not be considered available features unless implemented.

## Contributing

Contributions, suggestions, and bug reports are welcome.

To contribute:

1. Fork the repository.
2. Create a feature branch.
3. Implement and test your changes.
4. Commit your changes with a descriptive message.
5. Submit a pull request.

Please avoid committing secrets, credentials, environment files, or private configuration data.

## License

This project is licensed under the [PolyForm Noncommercial License 1.0.0](https://github.com/eshan868/x-fight/blob/master/LICENSE).
Free for personal, educational and other non-commercial use. Commercial use requires my permission.

Copyright © 2026 Muhammed Eshan P

See the [LICENSE](LICENSE) file for the complete license.
