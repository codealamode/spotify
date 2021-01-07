import lyricsgenius
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from os import getenv
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, session


load_dotenv()
SCOPE="user-library-read user-top-read"
SPOTIPY_CLIENT_ID=getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET=getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI=getenv("SPOTIPY_REDIRECT_URI")
GENIUS_ACCESS_TOKEN=getenv("GENIUS_ACCESS_TOKEN")


# Checks to see if token is valid and gets a new token if not
def get_token(session):
    """Checks to see if there's a valid token for the current session and/or 
        whether an existing token is expired. 
        If expired, it grabs the refresh token."""

    token_valid = False
    token_info = session.get("token_info", {})

    # Checking if the session already has a token stored
    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid

    # Checking if token has expired
    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    # Refreshing token if it has expired
    if (is_token_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(
            session.get('token_info').get('refresh_token')
        )

    token_valid = True
    return token_info, token_valid


def get_sp(session):
    """
    Creates spotify object to make API call. If the user has not yet 
    authorized in the current session, they are directed back to the home 
    page. If they have already authorized, a Spotify object with an access 
    token is created, which is then used to make the appropriate API call.
    """

    session["token_info"], authorized=get_token(session)
    if not authorized:
        return redirect("/")
    return spotipy.Spotify(auth=session.get('token_info').get('access_token'), 
                                            requests_timeout=10)


def create_spotify_oauth():
    """Helper function to create SpotifyOAuth object"""
  
    return SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri=SPOTIPY_REDIRECT_URI,            
            scope=SCOPE)


def get_lyrics(artist_names, track_names):
    """
    this docstring is epic - Trey
    Input:  artist_names - A list of artist names
            track_names - A list of track names

    Returns: A list of lyrics corresponding to each track 
    """
    genius=lyricsgenius.Genius(GENIUS_ACCESS_TOKEN)

    lyrics=[]
    for idx, track in enumerate(track_names):
        artist = genius.search_artist(artist_names[idx], max_songs=0)
        lyrics.append(artist.song(track).lyrics)
    return lyrics


def get_top_songs():
    sp = get_sp(session)

    # Get top 10 of user's recently listened to tracks
    # !BUG! A bug happens here if a user tries to access this route without
    #       being logged in...
    user_top_tracks = sp.current_user_top_tracks(limit=10, 
                                                    time_range="short_term"
                                                    )["items"]
                                                    
    # Get track ids for each track in user_top_tracks. Track id is needed 
    # to retrieve audio features for each of those tracks.
    top_track_ids =[track["id"] for track in user_top_tracks]
    top_track_features = sp.audio_features(top_track_ids)

    # Create features dataframe and drop all unnecessary features
    try:
        cols = ["type", "id", "uri", "track_href", "analysis_url"]
        features_df = pd.DataFrame(top_track_features).drop(columns=cols)
    except:
        return render_template("error.html",
                                type='0 - Empty Spotify')

    # Write the df to a csv file
    features_df.to_csv("features_df.csv", index=False)

    # Get list of artist names for each track in user_top_tracks. 
    # NOBUG: Some tracks have multiple artists. In those cases, we choose 
    #        just the first one to feed into get_lyrics()
    top_track_artists = [track["artists"][0]["name"] 
                            for track in user_top_tracks]

    # Get list of track names for each track in user_top_tracks
    top_track_names = [track["name"] for track in user_top_tracks]
    return top


if __name__ == "__main__":
    print('DEBUG MODE DETECTED FOR UTILS.PY - TESTING WITH DUMMY DATA')
    genius=lyricsgenius.Genius(GENIUS_ACCESS_TOKEN)
    artist = genius.search_artist("Britney Spears", max_songs=0)
    song=artist.song("Toxic")
    print(song.lyrics)
