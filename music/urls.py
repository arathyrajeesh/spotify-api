from django.urls import path
from . import views
from .auth_views import register_user, login_user
from django.contrib.auth import views as auth_views

urlpatterns = [
    # HTML pages
    path('', views.home, name='home'),
    path('search/', views.search_page, name='search_page'),
    path('favorites/', views.favorites_page, name='favorites_page'),
    path('login/', views.login_page, name='login_page'),
    path('register/', views.register_page, name='register_page'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login_page'), name='logout'),

    # API endpoints
    path('api/search/', views.search_song, name='search_song'),
    path('api/register/', register_user, name='register_user'),
    path('api/login/', login_user, name='login_user'),
    path('api/favorites/add/', views.add_favorite, name='add_favorite'),
    path('api/favorites/', views.list_favorites, name='list_favorites'),
    path('api/favorites/<int:favorite_id>/remove/', views.remove_favorite, name='remove_favorite'),
    path('api/history/', views.list_search_history, name='list_search_history'),
    path('api/history/clear/', views.clear_search_history, name='clear_search_history'),
]
