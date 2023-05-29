from django.contrib.auth.models import AbstractUser
from django.utils import timezone  # to show singapore time
from django.db import models


class User(AbstractUser):
    pass


class Post(models.Model):
    message = models.CharField(max_length=200)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="author")
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        format_string = "%d %b %Y %I:%M%p"
        # Foreign key..need to access User
        capitalized_user = self.user.username.capitalize()
        return f"{capitalized_user} posted {self.message} on {self.date_posted.strftime(format_string)}"


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower")
    user_follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="being_followed")

    def __str__(self):
        return f"{self.user} is following {self.user_follower}"


class Like(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_liking_post")
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="post_being_liked")

    def __str__(self):
        return f"{self.user} liked {self.post}"
