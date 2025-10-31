from django.urls import path
from .views import search_song

urlpatterns = [
    path('search/', search_song, name='search_song'),
]
