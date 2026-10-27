from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class user_profile(models.Model):
    user=models.OneToOneField(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    full_name=models.CharField(max_length=100)
    age=models.CharField()
    gamer_tag=models.CharField(max_length=100,unique=True)
    profile_image=models.ImageField(upload_to="profile_images/",blank=True,null=True)
    bio=models.TextField()
    youtube_link=models.CharField(blank=True)
    discode_link=models.CharField(blank=True)
    instagram_link=models.CharField(blank=True)
    xp=models.IntegerField(default=0)
    stats=models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

 
from django.db import models
from django.conf import settings


class CoinTransfer(models.Model):

    sender = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="sent_coin_transfers"
    )

    receiver = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="received_coin_transfers"
    )

    amount = models.PositiveBigIntegerField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.sender} sent "
            f"{self.amount} coins to "
            f"{self.receiver}"
        )


