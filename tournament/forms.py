from django import forms
from django.forms import ModelForm
from .models import *
from social.models import *
from django.db.models import Q
from django.contrib.auth import get_user_model
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from django.utils import timezone
from datetime import timedelta


User = get_user_model()


class Tournament_Register_form(ModelForm):

    starting_time = forms.DateTimeField(
        widget=forms.DateTimeInput(
            format="%Y-%m-%dT%H:%M",
            attrs={
                "type": "datetime-local",
                "class": "form-control",
            }
        ),
        input_formats=["%Y-%m-%dT%H:%M"],
    )

    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(
            format="%Y-%m-%dT%H:%M",
            attrs={
                "type": "datetime-local",
                "class": "form-control",
            }
        ),
        input_formats=["%Y-%m-%dT%H:%M"]
    )
    user_timezone = forms.CharField(required=False,widget=forms.HiddenInput())

    class Meta:
        model = Tournament

        exclude = [
            "owner",
            "match_report_upload_mode",
            "report_upload_users",
            "like",
            "players",
        ]

    def _convert_to_utc(self, value):
        user_timezone = self.data.get("user_timezone")

        if not user_timezone:
            return value

        try:
            user_tz = ZoneInfo(user_timezone)

            if timezone.is_aware(value):
                value = timezone.make_naive(
                    value,
                    timezone.get_current_timezone()
                )

            value = timezone.make_aware(
                value,
                user_tz
            )

            return value.astimezone(ZoneInfo("UTC"))

        except ZoneInfoNotFoundError:
            raise forms.ValidationError("Invalid timezone.")

    def clean_starting_time(self):
        value = self.cleaned_data["starting_time"]
        return self._convert_to_utc(value)

    def clean_end_time(self):
        value = self.cleaned_data["end_time"]
        return self._convert_to_utc(value)


class match_making_form(ModelForm):

    duration = forms.ChoiceField(
        choices=[
            ("0:05:00", "5 Minutes"),
            ("0:10:00", "10 Minutes"),
            ("0:15:00", "15 Minutes"),
            ("0:20:00", "20 Minutes"),
            ("0:30:00", "30 Minutes"),
            ("1:00:00", "1 Hour"),
        ],
        widget=forms.Select(
            attrs={
                "class": "form-select"
            }
        ))

    game = forms.ChoiceField(
        choices=[
            ("efootball", "eFootball"),
            ("fc", "FC Football"),
            ("other", "Other"),
        ],
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ))

    user_timezone = forms.CharField(required=False,widget=forms.HiddenInput())

    class Meta:
        model = Match
        exclude = [
            "winner_team",
            "tournament",
            "winner_user",
            "status"
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter match name"
                }
            ),
            "match_start_time": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={
                    "type": "datetime-local",
                    "class": "form-control"
                }
            ),
            "match_end_time": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={
                    "type": "datetime-local",
                    "class": "form-control"
                }
            ),
            "max_teams": forms.NumberInput(
                attrs={
                    "class": "form-control"
                }
            ),
            "teams": forms.CheckboxSelectMultiple(),
            "match_players": forms.CheckboxSelectMultiple(),
        }
        
    def clean_duration(self):
        value = self.cleaned_data["duration"]

        hours, minutes, seconds = map(int,value.split(":"))
        return timedelta(hours=hours,minutes=minutes,seconds=seconds)
    def clean_match_start_time(self):
        value = self.cleaned_data["match_start_time"]
        user_timezone = self.data.get("user_timezone")
        if not user_timezone:
            return value
        try:
            user_tz = ZoneInfo(user_timezone)
            if timezone.is_aware(value):
                value = timezone.make_naive(
                    value,
                    timezone.get_current_timezone()
                )
            value = timezone.make_aware(value,user_tz)
            return value.astimezone(ZoneInfo("UTC"))
        except ZoneInfoNotFoundError:
            raise forms.ValidationError("Invalid timezone.")

    

    def clean_match_end_time(self):
        value = self.cleaned_data["match_end_time"]
        user_timezone = self.data.get("user_timezone")

        if not user_timezone:
            return value

        try:
            user_tz = ZoneInfo(user_timezone)
            if timezone.is_aware(value):
                value = timezone.make_naive(
                    value,
                    timezone.get_current_timezone()
                )

            value = timezone.make_aware(value,user_tz)

            return value.astimezone(ZoneInfo("UTC"))

        except ZoneInfoNotFoundError:
            raise forms.ValidationError("Invalid timezone.")


class team_making_form(ModelForm):

    class Meta:
        model = Team
        exclude = [
            "captain",
            "user",
            "tournaments"
        ]
    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)

        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({
                "class": "form-control",
                "placeholder": field.label,
            })

        if user and "members" in self.fields:
            relations = GameMate.objects.filter(
                Q(user=user,status="accepted")|Q(mate=user,status="accepted"))
            gamemate_ids = []
            for relation in relations:
                if relation.user == user:
                    gamemate_ids.append(relation.mate.id)
                else:
                    gamemate_ids.append(relation.user.id)

            self.fields["members"].queryset = User.objects.filter(
                id__in=gamemate_ids
            )

            self.fields["members"].widget.attrs.update({
                "class": "form-control"
            })


class MatchScoreboardForm(ModelForm):

    class Meta:
        model = match_result_form
        fields = ["screenshot"]
class team_meeting_schedule_form(forms.ModelForm):
    user_timezone = forms.CharField(
        required=False,
        widget=forms.HiddenInput())

    class Meta:
        model = team_meeting

        exclude = [
            "team"
            ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Meeting name"
                }
            ),
            "password": forms.PasswordInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Meeting password"
                }
            ),
            "start_time": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={
                    "class": "form-control",
                    "type": "datetime-local"
                }
            ),
            "end_time": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={
                    "class": "form-control",
                    "type": "datetime-local"
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Meeting description",
                    "rows": 4
                }
            ),
            "notification_send": forms.CheckboxInput(
                attrs={
                    "class": "notification-checkbox"
                }
            ),
        }

    def _convert_to_utc(self, value):
        user_timezone = self.data.get("user_timezone")

        if not user_timezone:
            return value

        try:
            user_tz = ZoneInfo(user_timezone)

            if timezone.is_aware(value):
                value = timezone.make_naive(value,timezone.get_current_timezone())
            value = timezone.make_aware(value,user_tz)
            return value.astimezone(ZoneInfo("UTC"))

        except ZoneInfoNotFoundError:
            raise forms.ValidationError("Invalid timezone.")

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        if start_time:
            start_time = self._convert_to_utc(start_time)
            cleaned_data["start_time"] = start_time
        if end_time:
            end_time = self._convert_to_utc(end_time)
            cleaned_data["end_time"] = end_time

        if start_time and end_time:
            if end_time <= start_time:
                raise forms.ValidationError(
                    "Meeting end time must be after the start time."
                )

        return cleaned_data

class freindly_match_making_form(forms.ModelForm):

    duration = forms.ChoiceField(
        choices=[
            ("0:05:00", "5 Minutes"),
            ("0:10:00", "10 Minutes"),
            ("0:15:00", "15 Minutes"),
            ("0:20:00", "20 Minutes"),
            ("0:30:00", "30 Minutes"),
            ("1:00:00", "1 Hour"),
        ],
        widget=forms.Select(
            attrs={"class": "form-select"}
        ),
    )

    game = forms.ChoiceField(
        choices=[
            ("efootball", "eFootball"),
            ("fc", "FC Football"),
            ("other", "Other"),
        ],
        widget=forms.Select(
            attrs={"class": "form-select"}
        ),
    )

    loot_enable = forms.BooleanField(
        required=False,
        label="Enable Loot",
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
                "id": "id_loot_enable",
            }
        ),
    )

    loot = forms.IntegerField(
        required=False,
        min_value=1,
        label="Loot Amount (Coins)",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "id": "id_loot",
                "min": "1",
                "placeholder": "Enter loot amount",
            }
        ),
    )

    user_timezone = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )

    class Meta:
        model = Match

        fields = "__all__"

        exclude = [
            "winner_team",
            "tournament",
            "winner_user",
            "status",
            "teams",
            "max_teams",
            "friendly_match_room",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter match name",
                }
            ),
            "match_start_time": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={
                    "type": "datetime-local",
                    "class": "form-control",
                },
            ),
            "match_end_time": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={
                    "type": "datetime-local",
                    "class": "form-control",
                },
            ),
        }


    def __init__(self, *args, request_user=None, **kwargs):
        super().__init__(*args, **kwargs)
    
        self.request_user = request_user
    
        if "match_players" in self.fields:
            self.fields["match_players"].required = True
    
            if request_user and request_user.is_authenticated:
                gamemates = GameMate.objects.filter(
                    Q(user=request_user) | Q(mate=request_user),
                    status="accepted",
                )
    
                gamemate_ids = (
                    gamemates.filter(user=request_user)
                    .values_list("mate_id", flat=True)
                )
    
                other_ids = (
                    gamemates.filter(mate=request_user)
                    .values_list("user_id", flat=True)
                )
    
                self.fields["match_players"].queryset = (
                    User.objects.filter(
                        Q(id__in=gamemate_ids) |
                        Q(id__in=other_ids)
                    )
                    .exclude(id=request_user.id)
                    .distinct()
                )

    def clean_duration(self):
        value = self.cleaned_data["duration"]

        hours, minutes, seconds = map(
            int,
            value.split(":")
        )

        return timedelta(
            hours=hours,
            minutes=minutes,
            seconds=seconds,
        )

    def clean(self):
        cleaned_data = super().clean()

        loot_enabled = cleaned_data.get("loot_enable")
        loot_amount = cleaned_data.get("loot")

        if loot_enabled:
            if loot_amount is None:
                self.add_error(
                    "loot",
                    "Enter a loot amount when loot is enabled."
                )
            elif loot_amount < 1:
                self.add_error(
                    "loot",
                    "Loot amount must be greater than zero."
                )
        else:
            # Ignore any amount submitted while loot is disabled.
            cleaned_data["loot"] = 0

        start_time = cleaned_data.get("match_start_time")
        end_time = cleaned_data.get("match_end_time")

        if start_time and end_time and end_time <= start_time:
            self.add_error(
                "match_end_time",
                "Match end time must be after the start time."
            )

        return cleaned_data
    def clean_match_start_time(self):
        value = self.cleaned_data["match_start_time"]
        user_timezone = self.data.get("user_timezone")

        if not user_timezone:
            return value

        try:
            user_tz = ZoneInfo(user_timezone)

            if timezone.is_aware(value):
                value = timezone.make_naive(
                    value, timezone.get_current_timezone()
                )

            value = timezone.make_aware(value, user_tz)
            return value.astimezone(ZoneInfo("UTC"))

        except ZoneInfoNotFoundError:
            raise forms.ValidationError("Invalid timezone.")

    def clean_match_end_time(self):
        value = self.cleaned_data["match_end_time"]
        user_timezone = self.data.get("user_timezone")

        if not user_timezone:
            return value

        try:
            user_tz = ZoneInfo(user_timezone)

            if timezone.is_aware(value):
                value = timezone.make_naive(
                    value, timezone.get_current_timezone()
                )

            value = timezone.make_aware(value, user_tz)
            return value.astimezone(ZoneInfo("UTC"))

        except ZoneInfoNotFoundError:
            raise forms.ValidationError("Invalid timezone.")