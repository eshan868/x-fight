from django import forms
from django.forms import ModelForm
from .models import Tournament, Match,Team


class Tournament_Register_form(ModelForm):
    class Meta:

        model = Tournament

        fields = "__all__"


class match_making_form(ModelForm):
    class Meta:

        model = Match

        fields = "__all__"
        exclude=["winner"]


class team_making_form(ModelForm):
    class Meta:
        model = Team

        fields = "__all__"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():

           field.widget.attrs.update({
            "class": "form-control",
            "placeholder": field.label,
          })

        