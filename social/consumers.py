from channels.generic.websocket import WebsocketConsumer
from django.shortcuts  import get_object_or_404
from .models import *
import json
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import (AsyncJsonWebsocketConsumer,AsyncWebsocketConsumer)
from django.template.loader import render_to_string

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.chatroom = None
        self.user = self.scope["user"]
        self.chatroom_name = self.scope["url_route"]["kwargs"]["chatroom_name"]
        await self.accept()

        if not self.user.is_authenticated:
            print("chat: rejected, not authenticated")
            await self.close(code=4001)
            return
        
        self.chatroom = await self.get_chatroom()
        if self.chatroom is None:
            print("chat: rejected, room not found:", self.chatroom_name)
            await self.close(code=4004)
            return
    
        await self.channel_layer.group_add(self.chatroom_name, self.channel_name)
        print("chat: connected", self.user.username, self.chatroom_name)
    
        if await self.add_user_online():
            await self.update_online_count()
    
    async def disconnect(self, close_code):
        if getattr(self, "chatroom", None) is None:
            return
        await self.channel_layer.group_discard(self.chatroom_name, self.channel_name)
        if await self.remove_user_online():
            await self.update_online_count()

    async def receive(self, text_data):
        data = json.loads(text_data)
        body = (data.get("body") or "").strip()
        if not body:
            return
        message_id = await self.save_message(body)
        await self.channel_layer.group_send(self.chatroom_name,{
                "type": "message_handler",
                "message_id": message_id })

    async def message_handler(self, event):
        html = await self.render_message(event["message_id"])
        await self.send(text_data=html)

    async def online_count_handler(self, event):
        html = render_to_string(
            "social/partials/online_count_p.html",
            {"online_count": event["online_count"]})
        await self.send(text_data=html)

    async def update_online_count(self):
        online_count = await self.get_online_count()
        await self.channel_layer.group_send(
            self.chatroom_name,
            {
                "type": "online_count_handler",
                "online_count": online_count})
    async def message_deleted(self, event):
        await self.send(text_data=f'<div id="message-{event["message_id"]}" hx-swap-oob="delete"></div>')

    @database_sync_to_async
    def get_chatroom(self):
        return ChatGroup.objects.filter(group_name=self.chatroom_name).first()

    @database_sync_to_async
    def add_user_online(self):
        if self.chatroom.users_online.filter(pk=self.user.pk).exists():
            return False
        self.chatroom.users_online.add(self.user)
        return True

    @database_sync_to_async
    def remove_user_online(self):
        if not self.chatroom.users_online.filter(pk=self.user.pk).exists():
            return False
        self.chatroom.users_online.remove(self.user)
        return True

    @database_sync_to_async
    def get_online_count(self):
        return self.chatroom.users_online.count() - 1

    @database_sync_to_async
    def save_message(self, body):
        message = ChatGroupMessages.objects.create(body=body,author=self.user,group=self.chatroom,)

        if self.chatroom.is_private:
            text = f"{self.user.username} sent you a message"
            notification_type = "chat_message"
        elif self.chatroom.groupchat_name:
            text = f"{self.user.username} sent a message in {self.chatroom.groupchat_name}"
            notification_type = "group_message"
        else:
            return message.id

        for member in self.chatroom.members.exclude(pk=self.user.pk):
            Notification.objects.create(
                user=member,
                text=text,
                notification_type=notification_type,
                related_id=message.id)
            
        return message.id

    @database_sync_to_async
    def render_message(self, message_id):
        message = ChatGroupMessages.objects.select_related("author").get(id=message_id)
        return render_to_string("social/partials/group_chat_messages_p.html",{"chat_message": message, "user": self.user})
    
class CallConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"call_{self.room_id}"
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )
        await self.accept()

        await self.send_json({
            "type": "call_connected",
            "user_id": self.user.id,
            "username": self.user.username,
            "room_id": self.room_id})
        await self.channel_layer.group_send(self.room_group_name,{
                "type": "user_joined",
                "user_id": self.user.id,
                "username": self.user.username})
        
    async def disconnect(self, close_code):
        if not hasattr(self, "room_group_name"):
            return

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

        if self.user.is_authenticated:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "user_left",
                    "user_id": self.user.id,
                    "username": self.user.username})

    async def receive_json(self, content, **kwargs):
        message_type = content.get("type")

        if not message_type:
            return
        if message_type == "offer":
            await self.send_offer(content)
        elif message_type == "answer":
            await self.send_answer(content)
        elif message_type == "ice_candidate":
            await self.send_ice_candidate(content)
        elif message_type in ["mute", "camera", "hold", "ready"]:
            await self.send_call_status(content,message_type,)
        elif message_type == "leave":
            await self.leave_call()

    async def send_offer(self, content):
        await self.channel_layer.group_send(self.room_group_name,{
                "type": "webrtc_offer",
                "sender_id": self.user.id,
                "sender_name": self.user.username,
                "offer": content.get("offer"),
                "target_id": content.get("target_id")
                })

    async def send_answer(self, content):
        await self.channel_layer.group_send(self.room_group_name,{
                "type": "webrtc_answer",
                "sender_id": self.user.id,
                "sender_name": self.user.username,
                "answer": content.get("answer"),
                "target_id": content.get("target_id")
            })

    async def send_ice_candidate(self, content):
        await self.channel_layer.group_send(self.room_group_name,{
                "type": "webrtc_ice_candidate",
                "sender_id": self.user.id,
                "candidate": content.get("candidate"),
                "target_id": content.get("target_id")
            })

    async def send_call_status(self, content, status_type):
        await self.channel_layer.group_send(self.room_group_name,{
                "type": "call_status",
                "status_type": status_type,
                "sender_id": self.user.id,
                "sender_name": self.user.username,
                "value": content.get("value")
            })

    async def leave_call(self):
        await self.channel_layer.group_send(self.room_group_name,{
                "type": "call_user_left",
                "user_id": self.user.id,
                "username": self.user.username
            })

        await self.close()

    async def user_joined(self, event):
        if event["user_id"] == self.user.id:
            return

        await self.send_json({
            "type": "user_joined",
            "user_id": event["user_id"],
            "username": event["username"]
        })

    async def user_left(self, event):
        if event["user_id"] == self.user.id:
            return

        await self.send_json({
            "type": "user_left",
            "user_id": event["user_id"],
            "username": event["username"]
        })

    async def webrtc_offer(self, event):
        if event["sender_id"] == self.user.id:
            return

        if (event.get("target_id") and str(event["target_id"]) != str(self.user.id)):
            return
        await self.send_json({
            "type": "offer",
            "sender_id": event["sender_id"],
            "sender_name": event["sender_name"],
            "offer": event["offer"]
        })

    async def webrtc_answer(self, event):
        if event["sender_id"] == self.user.id:
            return

        if (event.get("target_id")and str(event["target_id"]) != str(self.user.id)):
            return
        
        await self.send_json({
            "type": "answer",
            "sender_id": event["sender_id"],
            "sender_name": event["sender_name"],
            "answer": event["answer"]
        })

    async def webrtc_ice_candidate(self, event):
        if event["sender_id"] == self.user.id:
            return

        if (event.get("target_id") and str(event["target_id"]) != str(self.user.id)):
            return

        await self.send_json({
            "type": "ice_candidate",
            "sender_id": event["sender_id"],
            "candidate": event["candidate"]
        })

    async def call_status(self, event):
        if event["sender_id"] == self.user.id:
            return

        await self.send_json({
            "type": "call_status",
            "status_type": event["status_type"],
            "sender_id": event["sender_id"],
            "sender_name": event["sender_name"],
            "value": event["value"]
        })

    async def call_user_left(self, event):
        if event["user_id"] == self.user.id:
            return

        await self.send_json({
            "type": "user_left",
            "user_id": event["user_id"],
            "username": event["username"]
        })


class GlobalCallConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        self.user_group_name = f"user_{self.user.id}"

        await self.channel_layer.group_add(self.user_group_name,self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "user_group_name"):
            await self.channel_layer.group_discard(self.user_group_name,self.channel_name)

    async def receive_json(self, content):
        message_type = content.get("type")

        if message_type == "accept_call":
            await self.handle_accept_call(content)
        elif message_type == "decline_call":
            await self.handle_decline_call(content)
        elif message_type == "cancel_call":
            await self.handle_cancel_call(content)

    async def handle_accept_call(self, content):
        caller_id = content.get("caller_id")
        room_id = content.get("room_id")
        call_type = content.get("call_type")
        chatroom_name = content.get("chatroom_name")

        if not caller_id or not room_id:
            return

        await self.channel_layer.group_send(f"user_{caller_id}",{
                "type": "call_accepted",
                "receiver_id": self.user.id,
                "receiver_name": self.user.username,
                "room_id": room_id,
                "call_type": call_type,
                "chatroom_name": chatroom_name
            })

    async def handle_decline_call(self, content):
        caller_id = content.get("caller_id")
        room_id = content.get("room_id")

        if not caller_id or not room_id:
            return

        await self.channel_layer.group_send(
            f"user_{caller_id}",
            {
                "type": "call_declined",
                "receiver_id": self.user.id,
                "receiver_name": self.user.username,
                "room_id": room_id
            })

    async def handle_cancel_call(self, content):
        receiver_id = content.get("receiver_id")
        room_id = content.get("room_id")

        if not receiver_id or not room_id:
            return

        await self.channel_layer.group_send(
            f"user_{receiver_id}",
            {
                "type": "call_cancelled",
                "caller_id": self.user.id,
                "caller_name": self.user.username,
                "room_id": room_id
            })

    async def incoming_call(self, event):
        await self.send_json({
            "type": "incoming_call",
            "caller_id": event["caller_id"],
            "caller_name": event["caller_name"],
            "room_id": event["room_id"],
            "call_type": event["call_type"],
            "chatroom_name": event.get("chatroom_name")
        })

    async def call_accepted(self, event):
        await self.send_json({
            "type": "call_accepted",
            "receiver_id": event["receiver_id"],
            "receiver_name": event["receiver_name"],
            "room_id": event["room_id"],
            "call_type": event["call_type"],
            "chatroom_name": event.get("chatroom_name")
        })

    async def call_declined(self, event):
        await self.send_json({
            "type": "call_declined",
            "receiver_id": event["receiver_id"],
            "receiver_name": event["receiver_name"],
            "room_id": event["room_id"]
        })

    async def call_cancelled(self, event):
        await self.send_json({
            "type": "call_cancelled",
            "caller_id": event["caller_id"],
            "caller_name": event["caller_name"],
            "room_id": event["room_id"]
        })