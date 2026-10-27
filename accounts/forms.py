from django import forms
from django.forms import ModelForm
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from . models import user_profile
import re
User = get_user_model()

class signup_form(ModelForm):

    username = forms.CharField(max_length=100)
    password = forms.CharField(
        widget=forms.PasswordInput(),
        label="Password",
        help_text=(
            "Use at least 8 characters, including an uppercase letter, "
            "a lowercase letter, a number, and a special character."
        )
    )
    email = forms.EmailField(max_length=200)

    class Meta:
        model = user_profile

        fields = [
            "full_name",
            "username",
            "email",
            "age",
            "gamer_tag",
            "bio",
            "youtube_link",
            "discode_link",
            "instagram_link",
            "profile_image",
            "password",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({
                "class": "form-control",
                "placeholder": field.label,
            })

        # Show password requirements below the password field.
        self.fields["password"].widget.attrs.update({
            "minlength": "8",
            "autocomplete": "new-password",
        })

    def clean_password(self):
        password = self.cleaned_data.get("password")

        if len(password) < 8:
            raise forms.ValidationError(
                "Password must contain at least 8 characters."
            )

        if not re.search(r"[A-Z]", password):
            raise forms.ValidationError(
                "Password must contain at least one uppercase letter."
            )

        if not re.search(r"[a-z]", password):
            raise forms.ValidationError(
                "Password must contain at least one lowercase letter."
            )

        if not re.search(r"\d", password):
            raise forms.ValidationError(
                "Password must contain at least one number."
            )

        if not re.search(r"[^A-Za-z0-9]", password):
            raise forms.ValidationError(
                "Password must contain at least one special character."
            )

        return password
class signin_form(forms.Form):
    
    username=forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput())    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control",
                "placeholder": field.label,
            })


class edit_profile_form(ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()

    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(),
        help_text="Leave blank to keep your current password."
    )

    class Meta:
        model = user_profile
        fields = [
            "full_name",
            "age",
            "gamer_tag",
            "bio",
            "youtube_link",
            "discode_link",
            "instagram_link",
            "profile_image",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        user = self.instance.user

        self.fields["username"].initial = user.username
        self.fields["email"].initial = user.email

        for name, field in self.fields.items():
            field.widget.attrs.update({
                "class": "form-control",
                "placeholder": field.label,
            })

    def clean_username(self):
        username = self.cleaned_data["username"]
        user = self.instance.user

        if User.objects.filter(username=username).exclude(pk=user.pk).exists():
            raise forms.ValidationError(
                "This username is already taken."
            )

        return username

    def clean_password(self):
        password = self.cleaned_data.get("password")
        user = self.instance.user

        # Blank password means keep the current password.
        if not password:
            return password

        # If the entered password matches the current password,
        # skip password validation.
        if user.check_password(password):
            return password

        # Validate only when the password is actually changing.
        try:
            validate_password(password, user=user)
        except ValidationError as error:
            raise forms.ValidationError(error.messages)

        return password

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user

        user.username = self.cleaned_data["username"]
        user.email = self.cleaned_data["email"]

        password = self.cleaned_data.get("password")

        # Change the password only if a different password was entered.
        if password and not user.check_password(password):
            user.set_password(password)

        if commit:
            user.save()
            profile.save()
            self.save_m2m()

        return profile