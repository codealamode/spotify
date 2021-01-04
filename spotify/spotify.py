import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from dotenv import load_dotenv
from os import getenv

load_dotenv()

scope = "user-library-read"

SPOTIPY_CLIENT_ID=getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET=getenv("SPOTIPY_CLIENT_SECRET")


# Prints the names of all the user's playlists
sp = spotipy.Spotify(auth_manager=SpotifyOAuth( redirect_uri="http://127.0.0.1:5000/callback",
                                               scope="user-library-read"))

results = sp.current_user_saved_tracks()
for idx, item in enumerate(results['items']):
    track = item['track']
    print(idx, track['artists'][0]['name'], " – ", track['name'])

playlists=sp.current_user_playlists()
for item in playlists['items']:
    print(item['name'])
