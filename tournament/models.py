from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta



class Tournament(models.Model):

    CATEGORY_CHOICES = [
        ("solo", "Solo"),
        ("team", "Team"),
    ]
    owner = models.ForeignKey(User, on_delete=models.CASCADE,related_name="owner",null=True,blank=True)
    admins=models.ManyToManyField(User,blank=True,related_name="tournament_admins")

    # in this the team field in in team model  trough relation it is connected check in team model  
    players=models.ManyToManyField(User,blank=True,related_name="tournament_players")

    name = models.CharField(max_length=100)

    starting_time = models.DateField()

    end_time = models.DateField()

    description = models.TextField()

    price = models.PositiveBigIntegerField(default=0)

    like = models.ManyToManyField(User,blank=True, related_name="tournament_like")

    entry_fee=models.PositiveBigIntegerField(blank=True,null=True,default=0)

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )
    match_report_upload_mode=models.CharField(
        max_length=30,
        choices=[
            ("owner","Owner,only"),
            ("select","Selected Users"), 
        ],
        default="owner"
    )
    report_upload_users = models.ManyToManyField(
        User,
        blank=True,
        related_name="report_upload_permission"
        
    )
    def __str__(self):
       return self.name



class Team(models.Model):
    user=models.ManyToManyField(
        User
    )
    tournaments = models.ManyToManyField(
        Tournament
    )

    name = models.CharField(
        max_length=100
    )

    max_players = models.IntegerField()

    captain = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="captained_teams"
    )

class team_meeting(models.Model):

    team = models.ForeignKey(
        Team,
        null=True,
        on_delete=models.CASCADE,
        related_name="team_meeting"
    )

    name = models.CharField(
        max_length=50,
        default="unknown"
    )

    password = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    start_time = models.DateTimeField(
        default=timezone.now
    )

    end_time = models.DateTimeField(
        null=True,
        blank=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    notification_send = models.BooleanField(
        default=True
    )
    status=models.CharField(
        max_length=30,
        choices=[
            ("waiting","waiting"),
            ("active","active"),
            ("finished","finished") 
        ],
        default="active"
    )


    def __str__(self):
        return self.name


     
    def __str__(self):
        return self.name


class Match(models.Model):

    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name="matches",
        null=True,
        blank=True
    )
    teams = models.ManyToManyField(Team,related_name="matches",blank=True)
    match_players=models.ManyToManyField(User,blank=True)

    winner_team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="won_team_matches"
    )

    winner_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="won_solo_matches"
    )

    name = models.CharField(
        max_length=100
    )

    max_teams = models.IntegerField(null=True,blank=True)

    game=models.CharField(
    max_length=100,
    null=True,
    blank=True
    )  

    match_start_time=models.DateTimeField(null=True)
    match_end_time=models.DateTimeField(null=True,blank=True)
    duration = models.DurationField(default=timedelta(minutes=5))
    loot=models.PositiveBigIntegerField(default=0,null=True,blank=True)
    loot_enable=models.BooleanField(default="False")
    status=models.CharField(
        max_length=20,choices=[
            ("scheduled", "Scheduled"),
            ("open", "Open"),
            ("countdown", "Countdown"),
            ("live", "Live"),
            ("finished", "Finished"),
        ],
        default="scheduled"
    )
    friendly_match_room=models.BooleanField(default=False)
    started_at=models.DateTimeField(null=True,blank=True)
    ended_at=models.DateTimeField(null=True,blank=True)

class match_player(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE,related_name="match_player")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined = models.BooleanField(default=False)
    ready = models.BooleanField(default=False)

class match_result_form(models.Model):
    STATUS_CHOICES = [
        ("submitted", "Submitted"),
        ("verified", "Verified"),
        ("disputed", "Disputed"),
    ]

    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name="friendly_submissions",
    )

    player = models.ForeignKey(
        User,
        null = True,
        blank = True,
        on_delete=models.CASCADE,
        related_name="friendly_match_submissions",
    )

    screenshot = models.ImageField(
        upload_to="match_report_images/",
        null=True
    )

    extracted_result = models.JSONField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="submitted",
    )

    submitted_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["match", "player"],
                name="unique_friendly_match_submission",
            )
        ]

    def __str__(self):
        return f"{self.player} - Match {self.match_id}"