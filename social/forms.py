from django.forms import ModelForm
from django import forms
from . models import *


class ChatMessageCreatorForm(ModelForm):
    class Meta:
        model=ChatGroupMessages
        fields=['body']
        widgets = {
            'body': forms.TextInput(attrs={
                'class': 'chat-input',
                'placeholder': 'Type a message...',
                'autocomplete': 'off',
            })
            }


class NewGroupForm(ModelForm):
    class Meta:
        model=ChatGroup
        fields=['groupchat_name']
        widgets={
            'groupchat_name':forms.TextInput(attrs={
                'placeholder':'Add name',
                'class':'group-name-input-field',
                'maxlength':300,
                'autofocus':True
            }),
        }