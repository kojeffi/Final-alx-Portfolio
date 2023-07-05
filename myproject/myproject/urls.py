from django.urls import path
from myapp.views import toggle_process, clear_word, video_feed

urlpatterns = [
    path('', toggle_process, name='toggle_process'),
    path('clear-word/', clear_word, name='clear_word'),
    path('video-feed/', video_feed, name='video_feed'),
]
