from django.urls import path
from . import views  
from .auth_views import register_user, login_user

urlpatterns = [
    path('search/', views.search_song, name='search_song'),                    
    path('register/', register_user, name='register_user'),                    
    path('login/', login_user, name='login_user'),                             
    path('favorites/add/', views.add_favorite, name='add_favorite'),           
    path('favorites/', views.list_favorites, name='list_favorites'),           
    path('favorites/<int:favorite_id>/remove/', views.remove_favorite, name='remove_favorite'),
    path('history/', views.list_search_history, name='list_search_history'),
    path('history/clear/', views.clear_search_history, name='clear_search_history'),

]
