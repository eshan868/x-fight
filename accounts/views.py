from django.shortcuts import render,redirect,get_object_or_404
from . forms import signup_form,signin_form,edit_profile_form
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from tournament.models import Team,Tournament,Match
from django.contrib import messages
from django.db.models import Q,Sum
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib.auth import update_session_auth_hash
from . models import *
from social.models import *

# Create your views here.
def signup(request):

        if request.method == "POST":
            form = signup_form(request.POST,request.FILES)

            if form.is_valid():
               username = form.cleaned_data["username"]
               user_exists = User.objects.filter(username=username)

               if user_exists.exists():
                    messages.error(request, "Username already exists.")
                    return render(request, "authentication/signup.html", {"form": form})
               
               user = User.objects.create_user(username=form.cleaned_data[ "username" ],password=form.cleaned_data["password"],email=form.cleaned_data["email"])
               profile = form.save(commit=False)
               profile.user = user
               profile.save()
               return redirect("home")
        else:
            form = signup_form()
            print(form.errors)

        return render(request,"authentication/signup.html", {"form":form})


def signin(request):

    if request.method == "POST":
         form=signin_form(request.POST)
         if form.is_valid():
              username=form.cleaned_data["username"]
              password=form.cleaned_data["password"]
              user = authenticate(request,username=username,password=password)

              if user is not None:
                   login(request,user)
                   return redirect("dashboard")

              else:
                   redirect("signin")
                   print(form.errors)
    else:
         form=signin_form()

    return render(request,"authentication/signin.html",{"form":form})

@login_required
def dashboard(request):
     team=Team.objects.filter(user=request.user)
     matches=Match.objects.filter(match_players=request.user)
     #print(team)
     profile=get_object_or_404(user_profile,user=request.user)
     tournament = Tournament.objects.filter(Q(players=request.user) | Q(team__user=request.user) ).distinct()
     #print(tournament)
     users=User.objects.all()
     game_mate=GameMate.objects.filter(Q(user=request.user) | Q(mate=request.user),status="accepted")
     joined_groups = ChatGroup.objects.filter(members=request.user)
     transfers = CoinTransfer.objects.filter( Q(sender=request.user) |Q(receiver=request.user)).select_related("sender","receiver")
     sent_coins = CoinTransfer.objects.filter( sender=request.user).aggregate(total=Sum("amount"))["total"] or 0
     received_coins = CoinTransfer.objects.filter(receiver=request.user ).aggregate(total=Sum("amount"))["total"] or 0
     
     context={
          "teams":team,
          "tournament": tournament,
          "profile":profile,
          "users":users ,
          "matches":matches,
          "game_mates":game_mate , 
          "joined_groups": joined_groups,
          "transfers": transfers,
          "sent_coins": sent_coins,
          "received_coins": received_coins,
     }
     
    
     return render(request,"user/dashboard.html",context)

@login_required
def signout(request):

    logout(request)

    return redirect("home")

@login_required
def coin_transfer(request):

    profile = get_object_or_404(user_profile,user=request.user)
    game_mate = GameMate.objects.filter(Q(user=request.user) | Q(mate=request.user),status="accepted")
    coins = profile.xp
    

    if request.method == "POST":

        recipient_id = request.POST.get("recipient_id")
        amount_value = request.POST.get("amount")
        recipient = get_object_or_404(User,id=recipient_id)

        if not recipient_id:
            return redirect("coin-transfer")
        try:
            amount = int(amount_value)
        except (TypeError, ValueError):
            return redirect("coin-transfer")

        if amount <= 0:
            return redirect("coin_transfer")

        if int(recipient_id) == request.user.id:

            return redirect("coin-transfer")
        
        is_game_mate = game_mate.filter(Q(user=recipient) | Q(mate=recipient)).exists()
        if not is_game_mate:
            return redirect("coint-ransfer")

        with transaction.atomic():
            sender_profile = (user_profile.objects.select_for_update().get(user=request.user))
            receiver_profile = (user_profile.objects.select_for_update().get(user=recipient))

            if sender_profile.xp < amount: 
                return redirect("coin-transfer")
            
            sender_profile.xp -= amount
            sender_profile.save(update_fields=["xp"])
            receiver_profile.xp += amount
            receiver_profile.save(update_fields=["xp"])

            CoinTransfer.objects.create(
                sender=request.user,
                receiver=recipient,
                amount=amount
            )
            Notification.objects.create(
               user=recipient,
               text=f"{request.user.username} sent you {amount} coins",
               notification_type="chat_message",
            )

        return redirect("coin-transfer")

    return render(request,"user/coin_transfer.html",{"coins": coins,"game_mate": game_mate,})

@login_required
def edit_profile(request):
    profile = request.user.profile

    if request.method == "POST":
        form = edit_profile_form(request.POST,request.FILES,instance=profile,)

        if form.is_valid():
            password_changed = bool(form.cleaned_data.get("password"))
            form.save()
            if password_changed:
                update_session_auth_hash(request, request.user)
            return redirect("dashboard")
    else:
        form = edit_profile_form(instance=profile)

    return render(request,"authentication/edit_profile.html",{"form": form},)

