from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Tournament(models.Model):

    CATEGORY_CHOICES = [
        ("solo", "Solo"),
        ("team", "Team"),
    ]

    name = models.CharField(max_length=100)

    starting_time = models.DateField()

    end_time = models.DateField()

    description = models.TextField()

    price = models.CharField(max_length=100)

    like = models.ManyToManyField(User,blank=True,)

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
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
    user=models.ManyToManyField(User,blank=True)

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

    max_teams = models.IntegerField()

    game=models.CharField(
    max_length=100,
    null=True,
    blank=True
    )  

    match_date=models.DateTimeField(default=timezone.now) 
    
    status=models.CharField(
        max_length=20,choices=[
            ("waiting","Waiting"),
            ("live","Live"),
            ("finished","Finished")
        ],
        default="waiting"
    )

    started_at=models.DateTimeField(null=True,blank=True)
    ended_at=models.DateTimeField(null=True,blank=True)

class match_player(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE,related_name="match_player")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined = models.BooleanField(default=False)
    ready = models.BooleanField(default=False)