# music/urls.py
from django.urls import path
from .views import search_song
from .auth_views import register_user, login_user

urlpatterns = [
    path('search/', search_song, name='search_song'),
    path('register/', register_user, name='register_user'),
    path('login/', login_user, name='login_user'),
]
