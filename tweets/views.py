from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, JsonResponse
from django.utils.http import is_safe_url
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from .models import Tweet
from .serializers import TweetSerializer, TweetActionSerializer, TweetCreateSerializer, RegisterSerializer

ALLOWED_HOSTS = settings.ALLOWED_HOSTS

# Landing
def landing_view(request):
    return render(request, 'pages/landing.html')

# Feed
def feed_view(request):
    context = {}
    return render(request, 'pages/feed.html', context)

# Login
@api_view(["POST"])
def login_view(request):
    username = request.POST.get('username', None)
    password = request.POST.get('password', None)
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('feed')
    else:
        messages.warning(request, "Login failed.")
        return redirect('feed')
# Logout
def logout_view(request):
    logout(request)
    return redirect('feed')

# Register
@api_view(["POST"])
def register_view(request):
    serializer = RegisterSerializer(data=request.POST)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return redirect('feed')
    messages.warning(request, "Account creation failed.")
    return redirect('feed')

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
        content = "remeowed@" + tweet.user.username + " > " + tweet.content
        new_tweet = Tweet.objects.create(user=request.user, parent=tweet, content=content)
        serializer = TweetSerializer(new_tweet)
        return Response(serializer.data, status=200)
    return Response({}, status=200)