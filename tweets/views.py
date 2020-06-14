from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, JsonResponse
from django.utils.http import is_safe_url
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .forms import TweetForm
from .models import Tweet
from .serializers import TweetSerializer, TweetActionSerializer, TweetCreateSerializer

ALLOWED_HOSTS = settings.ALLOWED_HOSTS

# Homepage
def home(request):
    context = {}
    return render(request, 'pages/home.html', context)

# Login
def login(request):
    return HttpResponse("TODO LOGIN")

# Register
def register(request):
    return HttpResponse("TODO REGISTER")

# Logout
def logout(request):
    return HttpResponse("TODO LOGOUT")

# REST Framework View
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def tweet_create_view(request):
    serializer = TweetCreateSerializer(data=request.POST)
    if serializer.is_valid(raise_exception=True):
        serializer.save(user=request.user )
        return Response(serializer.data, status=201)
    return Response({}, status=400)

@api_view(["GET"])
def tweet_list_view(request):
    qs = Tweet.objects.all()
    serializer = TweetSerializer(qs, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def tweet_detail_view(request, tweet_id):
    tweet = Tweet.objects.get(id=tweet_id)
    serializer = TweetSerializer(tweet)
    return Response(serializer.data)

@api_view(["DELETE","POST"])
@permission_classes([IsAuthenticated])
def tweet_delete_view(request, tweet_id):
    tweets = Tweet.objects.filter(id=tweet_id)
    if not tweets.exists():
        return Response({}, status=404)
    tweets = tweets.filter(user=request.user)
    if not tweets.exists():
        return Response({"message": "You cannot delete this tweet"}, status=401)
    tweet = tweets.first()
    tweet.delete()
    return Response({"message": "Tweet removed"}, status=200)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def tweet_action_view(request):
    serializer = TweetActionSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        data = serializer.validated_data
        id = data.get("id")
        action = data.get("action")
        content = data.get("content")
    tweet = Tweet.objects.get(id=id)
    if tweet is None:
        return Response({"message": "Tweet does not exist"}, status=404)
    
    if action == "like":
        tweet.likes.add(request.user)
        serializer = TweetSerializer(tweet)
        return Response(serializer.data, status=200)
    elif action == "unlike":
        tweet.likes.remove(request.user)
        serializer = TweetSerializer(tweet)
        return Response(serializer.data, status=200)
    elif action == "retweet":
        new_tweet = Tweet.objects.create(user=request.user, parent=tweet, content=content)
        serializer = TweetSerializer(new_tweet)
        return Response(serializer.data, status=200)
    return Response({}, status=200)