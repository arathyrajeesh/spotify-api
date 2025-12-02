import base64
import requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Favorite
from .serializers import FavoriteSerializer
from .models import SearchHistory


def get_spotify_token():
    auth_string = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_string.encode()).decode()

    url = "https://accounts.spotify.com/api/token"
    headers = {"Authorization": f"Basic {b64_auth}"}
    data = {"grant_type": "client_credentials"}

    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]


@api_view(['GET'])
def search_song(request):
    # Temporarily remove auth check for debugging
    # if not request.user.is_authenticated:
    #     return Response({"error": "Authentication required"}, status=401)

    query = request.GET.get('q')
    if not query:
        return Response({"error": "Please provide ?q=search_term"}, status=400)

    try:
        # Temporarily comment out for debugging
        # SearchHistory.objects.create(user=request.user, query=query)
        pass

        token = get_spotify_token()
        spotify_headers = {"Authorization": f"Bearer {token}"}
        spotify_url = f"https://api.spotify.com/v1/search?q={query}&type=track&limit=10"

        spotify_response = requests.get(spotify_url, headers=spotify_headers)

        if spotify_response.status_code != 200:
            return Response({
                "error": f"Spotify API error: {spotify_response.status_code}",
                "details": spotify_response.text
            }, status=500)

        spotify_data = spotify_response.json()

        if not spotify_data.get("tracks", {}).get("items"):
            return Response({
                "message": "No results found on Spotify.",
                "query": query,
                "total_results": spotify_data.get("tracks", {}).get("total", 0)
            })

        # Get the first track with a preview URL if possible
        tracks = spotify_data["tracks"]["items"]
        track = None

        # First try to find a track with preview
        for t in tracks:
            if t.get("preview_url"):
                track = t
                break

        # If no track with preview, use the first one
        if not track and tracks:
            track = tracks[0]

        if not track:
            return Response({"message": "No tracks found."})

        song_name = track["name"]
        artist_name = track["artists"][0]["name"]

        song_info = {
            "song": song_name,
            "artist": artist_name,
            "album": track["album"]["name"],
            "release_date": track["album"]["release_date"],
            "popularity": track["popularity"],
            "album_art": track["album"]["images"][0]["url"] if track["album"]["images"] else None,
            "preview_url": track.get("preview_url"),
        }

        return Response(song_info)

    except Exception as e:
        return Response({"error": str(e), "type": type(e).__name__}, status=500)


@api_view(['POST'])
def add_favorite(request):
    # Temporarily remove auth check for debugging
    # if not request.user.is_authenticated:
    #     return Response({"error": "Authentication required"}, status=401)

    # For testing without authentication, create or get a test user
    if not request.user.is_authenticated:
        from django.contrib.auth.models import User
        test_user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        user = test_user
    else:
        user = request.user

    serializer = FavoriteSerializer(data=request.data)
    if serializer.is_valid():
        song = serializer.validated_data['song']
        artist = serializer.validated_data['artist']
        if Favorite.objects.filter(user=user, song=song, artist=artist).exists():
            return Response({"message": "Already added to favorites."}, status=200)
        serializer.save(user=user)
        return Response({"message": "Added to favorites!"}, status=201)
    return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_favorites(request):
    favorites = Favorite.objects.filter(user=request.user)
    data = [
        {
            "id": fav.id,   
            "song": fav.song,
            "artist": fav.artist,
            "album": fav.album,
            "added_at": fav.added_at
        }
        for fav in favorites
    ]
    return Response({"favorites": data})


@api_view(['DELETE'])
def remove_favorite(request, favorite_id):
    # Temporarily remove auth check for debugging
    # if not request.user.is_authenticated:
    #     return Response({"error": "Authentication required"}, status=401)

    # For testing without authentication, use test user
    if not request.user.is_authenticated:
        from django.contrib.auth.models import User
        test_user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        user = test_user
    else:
        user = request.user

    try:
        favorite = Favorite.objects.get(id=favorite_id, user=user)
        favorite.delete()
        return Response(
            {"message": "Favorite removed successfully."},
            status=status.HTTP_204_NO_CONTENT
        )
    except Favorite.DoesNotExist:
        return Response(
            {"error": "Favorite not found."},
            status=status.HTTP_404_NOT_FOUND
        )
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_search_history(request):
    history = SearchHistory.objects.filter(user=request.user)[:10]
    data = [
        {"query": item.query, "searched_at": item.searched_at}
        for item in history
    ]
    return Response({"recent_searches": data})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_search_history(request):
    SearchHistory.objects.filter(user=request.user).delete()
    return Response({"message": "Search history cleared."})


# HTML Views for Frontend

@login_required
def home(request):
    return render(request, 'music/home.html')

@login_required
def search_page(request):
    return render(request, 'music/search.html')

@login_required
def favorites_page(request):
    # For testing, if user is not authenticated, show test user's favorites
    if not request.user.is_authenticated:
        from django.contrib.auth.models import User
        test_user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        favorites = Favorite.objects.filter(user=test_user)
    else:
        favorites = Favorite.objects.filter(user=request.user)
    return render(request, 'music/favorites.html', {'favorites': favorites})

def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'music/login.html')

def register_page(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = UserCreationForm()
    return render(request, 'music/register.html', {'form': form})
