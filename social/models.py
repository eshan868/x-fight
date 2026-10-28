from django.db import models
from django.contrib.auth.models import User
import shortuuid
import os
from django.conf import settings
# Create your models here.
class GameMate(models.Model):
    STATUS = (
        ("non_gamemate","Non GameMate"),
        ("pending","Pending"),
        ("accepted","Accepted"),
        ("rejected","Rejected"),
    )

    user=models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="gamemates"
    )

    mate=models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="non_gamemate"
    )
    created_at=models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, null=True, blank=True,on_delete=models.CASCADE ,related_name="notification_sender")
    text = models.TextField()

    notification_type = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    related_id = models.IntegerField(
        null=True,
        blank=True
    )
    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(auto_now_add=True)

class ChatGroup(models.Model):
    group_name=models.CharField(max_length=128,unique=True , default=shortuuid.uuid)
    groupchat_name=models.CharField(max_length=130,null=True,blank=True)
    admin=models.ManyToManyField(User, related_name="groupchats",blank=True,)
    users_online=models.ManyToManyField(User, related_name='online_in_groups',blank=True)
    members = models.ManyToManyField(User,related_name='chat_groups', blank=True)
    is_private=models.BooleanField(default=False)
    team = models.OneToOneField("tournament.Team",on_delete=models.CASCADE,null=True,blank=True,related_name="team_chat")

    def __str__(self):
        return self.group_name
class ChatMessageQuerySet(models.QuerySet):
    def visible_to(self, user):
        return self.filter(deleted_for_everyone=False).exclude(deleted_for=user)
class ChatGroupMessages(models.Model):
    group=models.ForeignKey(ChatGroup,related_name="chat_messages", on_delete=models.CASCADE)
    author=models.ForeignKey(User,on_delete=models.CASCADE)
    body=models.CharField(max_length=500,null=True,blank=True)
    file=models.FileField(upload_to="chat_files/",blank=True,null=True)
    created=models.DateTimeField(auto_now_add=True)
    message_type = models.CharField(max_length=30,default="normal")
    is_forwarded = models.BooleanField(default=False)
    deleted_for_everyone = models.BooleanField(default=False)
    deleted_for = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="hidden_chat_messages",
        blank=True,
    )
    objects = ChatMessageQuerySet.as_manager()

    @property
    def filename(self):
        if self.file:
            return os.path.basename(self.file.name)
        else:
            return None

    def __str__(self):
        if self.body:
            return f'{self.author.username} : {self.body}'
        elif self.file :
             return f'{self.author.username} : {self.file}'




    @property

    def is_image(self):
        if self.filename.lower().endswith((".jpg",".jpeg",".png",".gif",".svg",".webp")):
            return True
        else:
            return False 

