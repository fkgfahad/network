from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Follow(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='follower')
    follower = models.ForeignKey(
        User, models.CASCADE, related_name='following')


class Post(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='posts')
    content = models.CharField(max_length=512)
    date = models.DateTimeField(auto_now_add=True)

    def format(self, user=None):
        post = {
            'id': self.id,
            'content': self.content,
            'date': self.date.strftime("%b %-d %Y, %-I:%M %p"),
            'likes': Like.objects.filter(post=self).count(),
            'username': self.user.username,
        }
        if user != None and user.is_authenticated:
            post['liked'] = Like.objects.filter(user=user, post=self).exists()
        return post


class Like(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, models.CASCADE, related_name='likes')
