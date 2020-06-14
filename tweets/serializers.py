from django.conf import settings
from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Tweet

MAX_TWEET_LENGTH = settings.MAX_TWEET_LENGTH
TWEET_ACTION_OPTIONS = settings.TWEET_ACTION_OPTIONS

class TweetActionSerializer(serializers.Serializer):
    id = serializers.IntegerField() # Tweet ID
    action = serializers.CharField() # Action be it, like, unlike, retweet
    content = serializers.CharField(allow_blank=True, required=False)
    
    def validate_content(self, value):
        value = value.lower().strip() # Strips white spaces
        if not value in TWEET_ACTION_OPTIONS:
            raise serializers.ValidationError("This is not a valid action")
        return value

class TweetCreateSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField(read_only=True)
    user = serializers.SerializerMethodField("get_username")

    class Meta:
        model = Tweet
        fields = ['id', 'user', 'content', 'likes']

    def get_likes(self, obj):
        return obj.likes.count()

    def get_username(self, obj):
        return obj.user.username

    def validate_content(self, value):
        if len(value) > MAX_TWEET_LENGTH:
            raise serializers.ValidationError("This tweet is too long.")
        return value

# Read only serializer
class TweetSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField(read_only=True)
    user = serializers.SerializerMethodField("get_username")
    parent = TweetCreateSerializer(read_only=True)

    class Meta:
        model = Tweet
        fields = ['id', 'user', 'content', 'likes', 'is_retweet', 'parent']

    def get_likes(self, obj):
        return obj.likes.count()

    def get_username(self, obj):
        return obj.user.username

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User(**validated_data)
        # Hash the user's password.
        user.set_password(validated_data['password'])
        user.save()
        return user