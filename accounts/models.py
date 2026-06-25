from django.db import models

# Create your models here.
class user_profile(models.Model):
 
    full_name=models.CharField(max_length=100)
    age=models.CharField()
    gamer_tag=models.CharField(max_length=100,unique=True)
    profile_image=models.ImageField(upload_to="profile_images/",blank=True,null=True)
    bio=models.TextField()
    youtube_link=models.CharField(blank=True)
    discode_link=models.CharField(blank=True)
    instagram_link=models.CharField(blank=True)

    def __str__(self):
        return self.user.username

 
    


