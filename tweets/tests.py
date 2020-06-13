from django.contrib.auth.models import User
from django.test import TestCase

from rest_framework.test import APIClient

from .models import Tweet

# Create your tests here.
class TweetTestCase(TestCase):
    def setUp(self):
        self.userA = User.objects.create_user(username="userA", password="passwordA")
        self.userB = User.objects.create_user(username="userB", password="passwordB")
        self.userC = User.objects.create_user(username="userC", password="passwordC")

        Tweet.objects.create(user=self.userA, content="Tweet 1")
        Tweet.objects.create(user=self.userB, content="Tweet 2")
        Tweet.objects.create(user=self.userC, content="Tweet 3")

        self.currentCount = Tweet.objects.all().count()

    def test_tweet_created(self):
        tweet = Tweet.objects.create(user=self.userA, content="Test Tweet")
        self.assertEqual(tweet.id, 4)
        self.assertEqual(tweet.user, self.userA)

    #REST Framwork API for authentication
    def get_client(self):
        client = APIClient()
        client.login(username=self.userA.username, password="passwordA")
        return client

    def test_tweet_list(self):
        client = self.get_client()
        response = client.get("/api/tweets/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)

    def test_action_like(self):
        client = self.get_client()
        response = client.post("/api/tweets/action/", {"id": 1, "action": 'like'})
        self.assertEqual(response.status_code, 200)
        like_count = response.json().get("likes")
        self.assertEqual(like_count, 1)

    def test_action_unlike(self):
        client = self.get_client()
        response = client.post("/api/tweets/action/", {"id": 2, "action": 'like'})
        self.assertEqual(response.status_code, 200)
        response = client.post("/api/tweets/action/", {"id": 2, "action": "unlike"})
        self.assertEqual(response.status_code, 200)
        like_count = response.json().get("likes")
        self.assertEqual(like_count, 0)

    def test_action_retweet(self):
        client = self.get_client()
        response = client.post("/api/tweets/action/", {"id": 3, "action": "retweet"})
        self.assertEqual(response.status_code, 200)
        new_tweet_id = response.json().get("id")
        self.assertNotEqual(3, new_tweet_id)
        self.assertEqual(self.currentCount + 1, new_tweet_id)

    def test_tweet_create_api_view(self):
        client = self.get_client()
        response = client.post("/api/tweets/create/", {"content": "This is a new tweets"})
        self.assertEqual(response.status_code, 201)
        new_tweet_id = response.json().get("id")
        self.assertEqual(self.currentCount + 1, new_tweet_id)

    def test_tweet_detail_api_view(self):
        client = self.get_client()
        response = client.get("/api/tweets/1/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("id"), 1)
        response = client.get("/api/tweets/2/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("id"), 2)
        response = client.get("/api/tweets/3/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("id"), 3)

    def test_tweet_delete_api_view(self):
        client = self.get_client()
        response = client.delete("/api/tweets/1/delete/")
        self.assertEqual(response.status_code, 200)
        client = self.get_client()
        response = client.delete("/api/tweets/1/delete/")
        self.assertEqual(response.status_code, 404)
        response_incorrect_owner = client.delete("/api/tweets/3/delete/")
        self.assertEqual(response_incorrect_owner.status_code, 401)