from django.db import models
from django.conf import settings

import random

User = settings.AUTH_USER_MODEL

class TweetLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tweet = models.ForeignKey("Tweet", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

class Tweet(models.Model):
    # Hidden ID that django automatically creates. A primary key that is autoincrementing.
    parent = models.ForeignKey("self", null=True, on_delete=models.SET_NULL )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Add users to the likes
    # One user can have many tweets, a tweet can have many users(retweet)
    # Similar to above's foreignkey, but this one has a list of users because it's many
    likes = models.ManyToManyField(User, related_name="tweet_user", blank=True, through=TweetLike)
    content = models.TextField(blank=True, null=True)
    image = models.FileField(upload_to='images/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Very cool how this works, change the 'metadata' of the Tweet Model
        ordering = ['-id']

    @property
    def is_retweet(self):
        return self.parent != None

    '''
    def serialize(self):
        return {
            "id": self.id,
            "content": self.content,
            "likes": random.randint(0,100)
        } 
    '''