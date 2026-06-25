from django import forms
from django.forms import ModelForm


from . models import user_profile

class signup_form(ModelForm):

    username=forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput())
    email=forms.EmailField(max_length=200)
    

    class Meta:
        model=user_profile


        fields=["full_name",
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
            
class signin_form(forms.Form):
    
    username=forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput())    
    
