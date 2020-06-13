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

# Create a tweet
def tweet_create_view_pure_django(request):
    user = request.user
    if not request.user.is_authenticated:
        user = None
        if request.is_ajax():
            return JsonResponse({}, status=401)
        return redirect(settings.LOGIN_URL)
    form = TweetForm(request.POST or None)
    next_url = request.POST.get("next", None)
    if next_url is not None and is_safe_url(next_url, ALLOWED_HOSTS):
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = user
            obj.save()
            if request.is_ajax():
                return JsonResponse(obj.serialize(), status=201) # 201 is for created item
            form = TweetForm()
            return redirect(next_url)
        if form.errors:
            if request.is_ajax():
                return JsonResponse(form.errors, status=400)
    context = {
        "form": form
    }
    return render(request, 'components/form.html', context)

# List view
def tweet_list_view_pure_django(request):
    '''
    REST API VIEW
    RETURN JSON DATA
    CONSUMED BY JAVASCRIPT
    '''
    qs = Tweet.objects.all()
    tweets_list = [x.serialize() for x in qs]
    data = {
        "isUser": False,
        "response": tweets_list
    }
    return JsonResponse(data)

# Detail view
def tweet_detail_view_pure_django(request, tweet_id, *args, **kwargs):
    '''
    REST API VIEW
    RETURN JSON DATA
    CONSUMED BY JAVASCRIPT
    '''
    data = {
        "id": tweet_id,
        # "content": tweet.content,
        # "image_path" : tweet.image.url
    }
    status = 200
    try:
        tweet = Tweet.objects.get(id=tweet_id)
        data["content"] = tweet.content
    except:
        data["message"] = "Not found"
        status = 404

    return JsonResponse(data, status=status)
    