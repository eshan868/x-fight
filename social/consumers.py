from channels.generic.websocket import WebsocketConsumer
from django.shortcuts  import get_object_or_404
from .models import *
import json
from asgiref.sync import async_to_sync
from django.template.loader import render_to_string
from channels.generic.websocket import AsyncJsonWebsocketConsumer
class ChatConsumer(WebsocketConsumer):

    def connect(self):
        self.user=self.scope['user']
        self.chatroom_name=self.scope['url_route']['kwargs']['chatroom_name']
        self.chatroom=get_object_or_404(ChatGroup,group_name=self.chatroom_name)

        async_to_sync (self.channel_layer.group_add) (
            self.chatroom_name,self.channel_name
        )

        if self.user not in self.chatroom.users_online.all():
            self.chatroom.users_online.add(self.user)
            self.update_online_count()

        self.accept()
    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.chatroom_name,self.channel_name
        )
        if self.user in self.chatroom.users_online.all():
                    self.chatroom.users_online.remove(self.user)
                    self.update_online_count()
        
    def receive(self,text_data):
        text_data_json=json.loads(text_data)
        body=text_data_json['body']

        message=ChatGroupMessages.objects.create(
            body=body,
            author=self.scope['user'],
            group=self.chatroom
        )
        if self.chatroom.is_private:

            for member in self.chatroom.members.all():

                if member != self.user:
    
                    Notification.objects.create(
                        user=member,
                        text=f"{self.user.username} sent you a message",
                        notification_type="chat_message",
                        related_id=message.id
                    )
    
                    # print("Private chat notification created")


        elif self.chatroom.groupchat_name:

            group_name = self.chatroom.groupchat_name

            for member in self.chatroom.members.all():

                if member != self.user:

                    Notification.objects.create(
                        user=member,
                        text=f"{self.user.username} sent a message in {group_name}",
                        notification_type="group_message",
                        related_id=message.id
                    )
    
                # print("Group chat notification created")

        event={
            'type':'message_handler',
            'message_id':message.id
        }

        async_to_sync(self.channel_layer.group_send)(
            self.chatroom_name,event
        ) 

    def message_handler(self , event):
        message_id=event['message_id']
        message=get_object_or_404(ChatGroupMessages,id=message_id)
        context={
                'chat_message':message,
                'user':self.user,
        }
        html=render_to_string("social/partials/group_chat_messages_p.html",context=context)
        self.send(text_data=html)

    def update_online_count(self):
        online_count=self.chatroom.users_online.count() -1
        event={
             'type':'online_count_handler',
             'online_count':online_count

        }
        async_to_sync(self.channel_layer.group_send)(
                    self.chatroom_name,event
                ) 
    def online_count_handler(self,event):
        online_count=event['online_count']

        html=render_to_string("social/partials/online_count_p.html",{'online_count':online_count})
        self.send(text_data=html)




class CallConsumer(AsyncJsonWebsocketConsumer):
    """
    Handles WebRTC signaling for voice and video calls.

    Django Channels transfers signaling messages.
    The actual audio and video are handled by the
    frontend calling SDK.
    """

    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"call_{self.room_id}"
        self.user = self.scope["user"]

        # Only authenticated users can connect.
        if not self.user.is_authenticated:
            await self.close()
            return

        # Add this connection to the call room.
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        await self.accept()

        # Confirm connection to the current user.
        await self.send_json({
            "type": "call_connected",
            "user_id": self.user.id,
            "username": self.user.username,
            "room_id": self.room_id,
        })

        # Notify other users in the room.
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_joined",
                "user_id": self.user.id,
                "username": self.user.username,
            },
        )

    async def disconnect(self, close_code):
        if not hasattr(self, "room_group_name"):
            return

        # Remove the connection from the call room.
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

        # Notify other users.
        if self.user.is_authenticated:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "user_left",
                    "user_id": self.user.id,
                    "username": self.user.username,
                },
            )

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
            await self.send_call_status(
                content,
                message_type,
            )

        elif message_type == "leave":
            await self.leave_call()

    async def send_offer(self, content):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "webrtc_offer",
                "sender_id": self.user.id,
                "sender_name": self.user.username,
                "offer": content.get("offer"),
                "target_id": content.get("target_id"),
            },
        )

    async def send_answer(self, content):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "webrtc_answer",
                "sender_id": self.user.id,
                "sender_name": self.user.username,
                "answer": content.get("answer"),
                "target_id": content.get("target_id"),
            },
        )

    async def send_ice_candidate(self, content):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "webrtc_ice_candidate",
                "sender_id": self.user.id,
                "candidate": content.get("candidate"),
                "target_id": content.get("target_id"),
            },
        )

    async def send_call_status(self, content, status_type):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "call_status",
                "status_type": status_type,
                "sender_id": self.user.id,
                "sender_name": self.user.username,
                "value": content.get("value"),
            },
        )

    async def leave_call(self):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "call_user_left",
                "user_id": self.user.id,
                "username": self.user.username,
            },
        )

        await self.close()

    # =====================================================
    # GROUP EVENT HANDLERS
    # =====================================================

    async def user_joined(self, event):
        if event["user_id"] == self.user.id:
            return

        await self.send_json({
            "type": "user_joined",
            "user_id": event["user_id"],
            "username": event["username"],
        })

    async def user_left(self, event):
        if event["user_id"] == self.user.id:
            return

        await self.send_json({
            "type": "user_left",
            "user_id": event["user_id"],
            "username": event["username"],
        })

    async def webrtc_offer(self, event):
        if event["sender_id"] == self.user.id:
            return

        if (
            event.get("target_id")
            and str(event["target_id"]) != str(self.user.id)
        ):
            return

        await self.send_json({
            "type": "offer",
            "sender_id": event["sender_id"],
            "sender_name": event["sender_name"],
            "offer": event["offer"],
        })

    async def webrtc_answer(self, event):
        if event["sender_id"] == self.user.id:
            return

        if (
            event.get("target_id")
            and str(event["target_id"]) != str(self.user.id)
        ):
            return

        await self.send_json({
            "type": "answer",
            "sender_id": event["sender_id"],
            "sender_name": event["sender_name"],
            "answer": event["answer"],
        })

    async def webrtc_ice_candidate(self, event):
        if event["sender_id"] == self.user.id:
            return

        if (
            event.get("target_id")
            and str(event["target_id"]) != str(self.user.id)
        ):
            return

        await self.send_json({
            "type": "ice_candidate",
            "sender_id": event["sender_id"],
            "candidate": event["candidate"],
        })

    async def call_status(self, event):
        if event["sender_id"] == self.user.id:
            return

        await self.send_json({
            "type": "call_status",
            "status_type": event["status_type"],
            "sender_id": event["sender_id"],
            "sender_name": event["sender_name"],
            "value": event["value"],
        })

    async def call_user_left(self, event):
        if event["user_id"] == self.user.id:
            return

        await self.send_json({
            "type": "user_left",
            "user_id": event["user_id"],
            "username": event["username"],
        })



class GlobalCallConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        self.user_group_name = f"user_{self.user.id}"

        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "user_group_name"):
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )

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

        await self.channel_layer.group_send(
            f"user_{caller_id}",
            {
                "type": "call_accepted",
                "receiver_id": self.user.id,
                "receiver_name": self.user.username,
                "room_id": room_id,
                "call_type": call_type,
                "chatroom_name": chatroom_name,
            }
        )

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
                "room_id": room_id,
            }
        )

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
                "room_id": room_id,
            }
        )

    async def incoming_call(self, event):
        await self.send_json({
            "type": "incoming_call",
            "caller_id": event["caller_id"],
            "caller_name": event["caller_name"],
            "room_id": event["room_id"],
            "call_type": event["call_type"],
            "chatroom_name": event.get("chatroom_name"),
        })

    async def call_accepted(self, event):
        await self.send_json({
            "type": "call_accepted",
            "receiver_id": event["receiver_id"],
            "receiver_name": event["receiver_name"],
            "room_id": event["room_id"],
            "call_type": event["call_type"],
            "chatroom_name": event.get("chatroom_name"),
        })

    async def call_declined(self, event):
        await self.send_json({
            "type": "call_declined",
            "receiver_id": event["receiver_id"],
            "receiver_name": event["receiver_name"],
            "room_id": event["room_id"],
        })

    async def call_cancelled(self, event):
        await self.send_json({
            "type": "call_cancelled",
            "caller_id": event["caller_id"],
            "caller_name": event["caller_name"],
            "room_id": event["room_id"],
        })