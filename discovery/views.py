from django.shortcuts import render
from tournament.models import Tournament


# Create your views here.

def event_display(request):
    events=Tournament.objects.all()
    return render(request,"display/event_display.html",{"event":events})
