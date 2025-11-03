import base64
import requests
from django.conf import settings
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
@permission_classes([IsAuthenticated])
def search_song(request):
    query = request.GET.get('q')
    if not query:
        return Response({"error": "Please provide ?q=search_term"}, status=400)

    try:
        SearchHistory.objects.create(user=request.user, query=query)

        token = get_spotify_token()
        spotify_headers = {"Authorization": f"Bearer {token}"}
        spotify_url = f"https://api.spotify.com/v1/search?q={query}&type=track&limit=1"

        spotify_response = requests.get(spotify_url, headers=spotify_headers)
        spotify_data = spotify_response.json()

        if not spotify_data["tracks"]["items"]:
            return Response({"message": "No results found on Spotify."})

        track = spotify_data["tracks"]["items"][0]
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
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_favorite(request):
    serializer = FavoriteSerializer(data=request.data)
    if serializer.is_valid():
        song = serializer.validated_data['song']
        artist = serializer.validated_data['artist']
        if Favorite.objects.filter(user=request.user, song=song, artist=artist).exists():
            return Response({"message": "Already added to favorites."}, status=200)
        serializer.save(user=request.user)
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
@permission_classes([IsAuthenticated])
def remove_favorite(request, favorite_id):
    try:
        favorite = Favorite.objects.get(id=favorite_id, user=request.user)
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
