from django.contrib import admin
from django.urls import path

from tweets import views

urlpatterns = [
    path('', views.tweet_list_view, name="list"),
    path('action/', views.tweet_action_view, name="action"),
    path('create/', views.tweet_create_view, name="create"),
    path('<int:tweet_id>/', views.tweet_detail_view, name='detail'),
    path('<int:tweet_id>/delete/', views.tweet_delete_view, name="delete")
]
