from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from myapp import views
from myapp.views import base
from myapp.views import about
from myapp.views import index
from myapp.views import services
from myapp.views import login
from myapp.views import dashboard
from django.contrib import admin
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('base/', views.base, name='base'),
    path('about/', about, name='about'),
    path('login/', views.custom_login, name='login'),
    path('services/', services, name='services'),
    path('registration/', views.registration, name='registration'),
    path('login/', views.login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('toggle_process', views.toggle_process, name='toggle_process'),
    path('clear_word/', views.clear_word, name='clear_word'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('save_recognized_alphabets/', views.save_recognized_alphabets, name='save_recognized_alphabets'),
    path('view_recognized_alphabets/', views.view_recognized_alphabets, name='view_recognized_alphabets'),
    path('clear_recognized_alphabets/', views.clear_recognized_alphabets, name='clear_recognized_alphabets'),
]

# Serving static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
