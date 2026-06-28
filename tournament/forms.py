from django import forms
from django.forms import ModelForm
from .models import Tournament, Match


class Tournament_Register_form(ModelForm):
    class Meta:

        model = Tournament

        fields = "__all__"


class match_making_form(ModelForm):
    class Meta:

        model = Match

        fields = "__all__"


class team_making_form(ModelForm):
    class Meta:
        model = Match

        fields = "__all__"
