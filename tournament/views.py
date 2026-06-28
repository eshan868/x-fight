from django.shortcuts import render,redirect
from . forms import Tournament_Register_form
# Create your views here.
def tournament_making(request):
    if request.POST:
        form=Tournament_Register_form(request.POST)
        if form.is_valid():
            tournament=form.save()
            tournament.save()
            return redirect("dashboard")
    else:
        form=Tournament_Register_form()
        print(form.errors)

    return render(request,"arena/tournament_making.html",{"form":form})

def team_making(request):
    if request.POST:
        form=team_making(request.POST)
        if form.is_valid():
            team=form.save()
            team.save()
            return redirect("dashboard")
    else:
        form=Tournament_Register_form()
        print(form.errors)

    return render(request,"arena/tournament_making.html",{"form":form})
