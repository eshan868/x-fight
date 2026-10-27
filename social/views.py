from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse,JsonResponse,Http404
from tournament.models import Team
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from accounts.models import user_profile,User
from django.db.models.functions import Random
from . models import *
import json
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib import messages
from . forms import *
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .services.token import create_zego_token
from django.conf import settings
import secrets

def leaderboard(request):
    profile=user_profile.objects.order_by("-stats",Random())

    return render(request,"social/leaderboard.html",{"profile":profile})
@login_required
def game_mate(request, user_id, mate_id):

    if user_id and mate_id:

        mate = get_object_or_404(User, id=mate_id)

        existing = GameMate.objects.filter(
            Q(user=request.user, mate=mate) |
            Q(user=mate, mate=request.user)
        ).first()

        if existing:

            messages.warning(
                request,
                "Game Mate request already exists."
            )

            return redirect("dashboard")


        game_mate = GameMate.objects.create(
            user=request.user,
            mate=mate,
            status="pending"
        )


        # Create notification for the receiver
        Notification.objects.create(
            user=mate,
            text=f"{request.user.username} sent you a game mate request",
            notification_type="game_mate_request",
            related_id=game_mate.id
        )


    return redirect("dashboard")


# =========================================================
# ACCEPT GAME MATE
# =========================================================

@login_required
def accept_game_mate(request, request_id):

    game_mate = get_object_or_404(
        GameMate,
        id=request_id
    )


    # Make sure the logged-in user is the receiver
    if game_mate.mate != request.user:

        messages.error(
            request,
            "You cannot accept this request."
        )

        return redirect("dashboard")


    # Accept request
    game_mate.status = "accepted"
    game_mate.save()


    # Delete the related notification
    Notification.objects.filter(
        user=request.user,
        notification_type="game_mate_request",
        related_id=game_mate.id
    ).delete()


    messages.success(
        request,
        "Game Mate request accepted."
    )


    return redirect("dashboard")


# =========================================================
# REJECT GAME MATE
# =========================================================

@login_required
def reject_game_mate(request, request_id):

    game_mate = get_object_or_404(
        GameMate,
        id=request_id
    )


    # Make sure the logged-in user is the receiver
    if game_mate.mate != request.user:

        messages.error(
            request,
            "You cannot reject this request."
        )

        return redirect("dashboard")


    # Delete related notification first
    Notification.objects.filter(
        user=request.user,
        notification_type="game_mate_request",
        related_id=game_mate.id
    ).delete()


    # Delete GameMate request
    game_mate.delete()


    messages.success(
        request,
        "Game Mate request rejected."
    )


    return redirect("dashboard")


# =========================================================
# CLEAR ALL NOTIFICATIONS
# =========================================================

@login_required
def clear_all_notifications(request):

    Notification.objects.filter(
        user=request.user
    ).delete()


    messages.success(
        request,
        "All notifications cleared."
    )


    return redirect("dashboard")
@login_required
def chat_view(request, chatroom_name='public'):
    chat_group=get_object_or_404(ChatGroup, group_name=chatroom_name)
    group_messages=ChatGroupMessages.objects.filter(group=chat_group)
    form=ChatMessageCreatorForm()
    game_mates=GameMate.objects.filter(
            Q(user=request.user) | Q(mate=request.user),
              status="accepted"
         )
    joined_groups = ChatGroup.objects.filter(
            members=request.user
        )

    game_mate=None
    if chat_group.is_private:
        if request.user not in chat_group.members.all():
            raise Http404()
        for member in chat_group.members.all():
            if member != request.user:
                game_mate=member
                break
    if chat_group.groupchat_name:
        if request.user not in chat_group.members.all():
            chat_group.members.add(request.user)
        

    if request.method == "POST":
       
        form = ChatMessageCreatorForm(request.POST)

        if form.is_valid():
            message = form.save(commit=False)
            message.author = request.user
            message.group = chat_group
            message.save()

            if request.headers.get("HX-Request"):
                return render(
                    request,
                    "social/partials/group_chat_messages_p.html", {"chat_message": message})
        
    context={
        "chat_messages":group_messages,
        "form":form,
        "game_mate":game_mate,
        "game_mates":game_mates,
        'chatroom_name':chatroom_name,
        'chat_group':chat_group,
        'joined_groups':joined_groups
    }

    return render(request,"social/group_chat.html", context)
@login_required
def get_or_create_chatroom(request, username):

    if request.user.username == username:
        return redirect('dashboard')
    
    game_mate = get_object_or_404(User, username=username)
    my_chatrooms = request.user.chat_groups.filter(is_private=True)
    chatroom = None

    if my_chatrooms.exists():
        for room in my_chatrooms:

            if game_mate in room.members.all():
                chatroom = room
                break

    if chatroom is None:
        chatroom = ChatGroup.objects.create(is_private=True)
        chatroom.members.add(game_mate, request.user)

    return redirect('chatroom', chatroom.group_name)
@login_required
def create_groupchat(request):
    form=NewGroupForm()
    if request.method == 'POST':
        form=NewGroupForm(request.POST)
        if form.is_valid():
            new_groupchat=form.save(commit=False)
            new_groupchat.save()
            new_groupchat.admin.add(request.user)
            new_groupchat.members.add(request.user)
            
            return redirect('chatroom',new_groupchat.group_name)


    
    return render(request,'social/create_groupchat.html',{'form':form})
@login_required
def group_details(request,chatgroup_room):
    chat_group=get_object_or_404(ChatGroup, group_name=chatgroup_room)
    member=chat_group.members.all()

    if request.method == "POST":
        action=request.POST['action']
        user_id=request.POST['user_id']
        user=get_object_or_404(User,id=user_id)
        if chat_group.admin.filter(id=request.user.id).exists():
            if action == "remove":
                chat_group.members.remove(user)
            elif action == "make_admin":
                chat_group.admin.add(user)
            if action == "remove_admin":
                chat_group.admin.remove(user)

        return redirect("chat-group-detail",chatgroup_room=chat_group.group_name)

    return render(request,"social/group-details.html",{'chat_group':chat_group ,'member':member})


@login_required
def send_group_invite(request, group_name, mate_id ):
     
    gm = get_object_or_404(User, id=mate_id)
    
    private_group = ChatGroup.objects.filter(
        is_private=True,
        members=request.user
        ).filter(
        members=gm
        ).first()
    
    if not private_group:
        private_group = ChatGroup.objects.create(is_private=True)
        private_group.members.add(request.user, gm)
    
    ChatGroupMessages.objects.create(
        group=private_group,
        author=request.user,
        body=group_name,
        message_type="group_invite"
    )

    return redirect("chatroom",chatroom_name=group_name )

@login_required
def chat_file_upload(request, chatroom_name):
    chat_group = get_object_or_404( ChatGroup, group_name=chatroom_name)
    if request.method == "POST":
        file = request.FILES.get("file")
        if not file:
            return HttpResponse("No file selected", status=400)
        message = ChatGroupMessages.objects.create(
            file=file,
            author=request.user,
            group=chat_group,
            message_type="normal",
        )
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            chatroom_name,
            {
                "type": "message_handler",
                "message_id": message.id,
            }
        )
        return HttpResponse("")
    return HttpResponse("Invalid request", status=400)


@login_required
def zego_token(request):
    user_id = str(request.user.id)

    token = create_zego_token(
        user_id=user_id,
        expires_in=3600,
    )

    return JsonResponse({
        "app_id": int(settings.ZEGO_APP_ID),
        "user_id": user_id,
        "token": token,
    })





# =========================================================
# SIMPLE GAME MATE CALL SYSTEM
# =========================================================
@login_required
def send_user_call_event(user_id, event):
    """
    Send a call invitation to a specific user.
    """

    channel_layer = get_channel_layer()

    async_to_sync(
        channel_layer.group_send
    )(
        f"user_{user_id}",
        event,
    )

@login_required
@require_POST
def start_call(request):
    """
    Start a group voice or video call.
    """

    try:
        data = json.loads(
            request.body.decode("utf-8")
        )

        chatroom_name = data["chatroom_name"]

        call_type = data.get(
            "call_type",
            "video",
        )

    except (
        json.JSONDecodeError,
        KeyError,
        TypeError,
    ):
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid call data.",
            },
            status=400,
        )

    if call_type not in ["voice", "video"]:
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid call type.",
            },
            status=400,
        )

    # Find the chat group.
    chat_group = ChatGroup.objects.filter(
        group_name=chatroom_name
    ).first()

    if not chat_group:
        return JsonResponse(
            {
                "success": False,
                "message": "Chat group not found.",
            },
            status=404,
        )

    # Check whether the caller belongs to this group.
    is_member = chat_group.members.filter(
        id=request.user.id
    ).exists()

    if not is_member:
        return JsonResponse(
            {
                "success": False,
                "message": "You are not a member of this group.",
            },
            status=403,
        )

    # Retrieve all members except the caller.
    receivers = chat_group.members.exclude(
        id=request.user.id
    )

    if not receivers.exists():
        return JsonResponse(
            {
                "success": False,
                "message": "No other members found in this group.",
            },
            status=400,
        )

    # Create one shared room ID.
    room_id = (
        f"gamearena_{secrets.token_urlsafe(16)}"
    )

    # Store receiver IDs for cancellation and frontend use.
    receiver_ids = list(
        receivers.values_list(
            "id",
            flat=True,
        )
    )

    # Send the same call invitation to every receiver.
    for receiver in receivers:

        send_user_call_event(
            receiver.id,
            {
                "type": "incoming_call",

                "caller_id": request.user.id,

                "caller_name": request.user.username,

                "room_id": room_id,

                "call_type": call_type,

                "chatroom_name": chatroom_name,
            },
        )

    return JsonResponse({
        "success": True,

        "room_id": room_id,

        "call_type": call_type,

        "chatroom_name": chatroom_name,

        "receiver_ids": receiver_ids,

        "message": "Group call invitation sent.",
    })  

@login_required
def calling_room(request):
    """
    Open the ZEGOCLOUD room using the shared room ID.
    """

    room_id = request.GET.get("room_id")

    call_type = request.GET.get(
        "call_type",
        "video",
    )

    if not room_id:
        return JsonResponse(
            {
                "success": False,
                "message": "Room ID is missing.",
            },
            status=400,
        )

    if call_type not in ["voice", "video"]:
        call_type = "video"

    return render(
        request,
        "social/calling_room.html",
        {
            "room_id": room_id,
            "call_type": call_type,
        },
    )

@login_required
def stats(request):
    user = get_object_or_404(user_profile, user=request.user)

    current_xp = user.xp
    current_stats = user.stats

    if request.method == "POST":

        action = request.POST.get("action")

        if action == "package":
            package = request.POST.get("package")

            if package not in ("starter", "pro", "elite"):
                return JsonResponse({
                    "success": False,
                    "message": "Invalid package selected."
                }, status=400)

            if package == "starter":
                if current_xp < 100:
                    return JsonResponse({
                        "success": False,
                        "message": "Insufficient balance. You need 100 coins."
                    }, status=400)

                user.xp -= 100
                user.stats += 80
                user.save(update_fields=["xp", "stats"])

                return JsonResponse({
                    "success": True,
                    "message": (
                        f"Stats successfully transferred to "
                        f"{request.user.username}! "
                        "Starter package: 80 stats added."
                    )
                })

            if package == "pro":
                if current_xp < 250:
                    return JsonResponse({
                        "success": False,
                        "message": "Insufficient balance. You need 250 coins."
                    }, status=400)

                user.xp -= 250
                user.stats += 200
                user.save(update_fields=["xp", "stats"])

                return JsonResponse({
                    "success": True,
                    "message": (
                        f"Stats successfully transferred to "
                        f"{request.user.username}! "
                        "Pro package: 200 stats added."
                    )
                })

            if package == "elite":
                if current_xp < 500:
                    return JsonResponse({
                        "success": False,
                        "message": "Insufficient balance. You need 500 coins."
                    }, status=400)

                user.xp -= 500
                user.stats += 450
                user.save(update_fields=["xp", "stats"])

                return JsonResponse({
                    "success": True,
                    "message": (
                        f"Stats successfully transferred to "
                        f"{request.user.username}! "
                        "Elite package: 450 stats added."
                    )
                })

        elif action == "custom":
            coins = request.POST.get("coins")

            try:
                coin = int(coins)
            except (TypeError, ValueError):
                return JsonResponse({
                    "success": False,
                    "message": "Please enter a valid coin amount."
                }, status=400)

            if coin < 5:
                return JsonResponse({
                    "success": False,
                    "message": "You need at least 5 coins."
                }, status=400)

            stat = coin // 5

            if current_xp < coin:
                return JsonResponse({
                    "success": False,
                    "message": "Insufficient balance."
                }, status=400)

            user.xp -= coin
            user.stats += stat
            user.save(update_fields=["xp", "stats"])

            return JsonResponse({
                "success": True,
                "message": (
                    f"Custom purchase successful for "
                    f"{request.user.username}! "
                    f"{stat} stats added for {coin} coins."
                )
            })

        return JsonResponse({
            "success": False,
            "message": "Invalid purchase action."
        }, status=400)

    return render(request, "social/stats.html")