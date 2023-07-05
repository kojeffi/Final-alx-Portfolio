from django.urls import path
from . import views

urlpatterns = [
    path('', views.toggle_process, name='toggle_process'),
    path('clear-word/', views.clear_word, name='clear_word'),
    path('video-feed/', views.video_feed, name='video_feed'),
    path('video_feed/', views.video_feed, name='video_feed'),
]
