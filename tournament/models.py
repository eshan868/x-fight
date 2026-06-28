from django.db import models
from django.contrib.auth.models import User


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

    like = models.IntegerField(default=0)

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )


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


class Match(models.Model):

    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE
    )

    winner = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
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