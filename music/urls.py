from django.urls import path
from . import views  
from .auth_views import register_user, login_user

urlpatterns = [
    path('search/', views.search_song, name='search_song'),
    path('register/', register_user, name='register_user'),
    path('login/', login_user, name='login_user'),
    path('favorites/add/', views.add_favorite, name='add_favorite'),  
    path('favorites/', views.list_favorites, name='list_favorites'), 
    path('favorites/<int:song_id>/remove/', views.remove_favorite, name='remove_favorite'),
    path('favorites/search/', views.search_favorites, name='search_favorites'),

]
