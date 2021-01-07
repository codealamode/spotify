import lyricsgenius
import pandas as pd
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from os import getenv
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, session
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors


load_dotenv()
SCOPE="user-library-read user-top-read"
FEATURE_NAMES=["danceability", "energy", "key", "loudness", "mode", "speechiness", "acousticness", 
                "instrumentalness", "liveness","valence", "tempo", "duration_ms"]
SPOTIPY_CLIENT_ID=getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET=getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI=getenv("SPOTIPY_REDIRECT_URI")
GENIUS_ACCESS_TOKEN=getenv("GENIUS_ACCESS_TOKEN")


# Checks to see if token is valid and gets a new token if not
def get_token(session):
    """
    Checks to see if there's a valid token for the current session and/or 
    whether an existing token is expired. 
    If expired, it grabs the refresh token.
    """

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
    """Helper function to create SpotifyOAuth object."""
  
    return SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri=SPOTIPY_REDIRECT_URI,            
            scope=SCOPE)


def get_lyrics(artists, songs):
    """
    Input:  artist_names - A list of artist names
            track_names - A list of track names

    Returns: A list of lyrics corresponding to each track 
    """
    genius=lyricsgenius.Genius(GENIUS_ACCESS_TOKEN)
    lyrics = [genius.search_song(song, artist).lyrics for (song, artist) in zip(songs, artists)]
    return lyrics


def normalize_data(df):
    """Normalizes a dataframe."""

    scaler=MinMaxScaler()
    df[FEATURE_NAMES] = scaler.fit_transform(df[FEATURE_NAMES])
    return df


def bad_recs(features_df, data_df):
    """
    Input: features_df - the dataframe of audio features for the user's top tracks
            data_df - the song dataset

    Returns: Names of the 10 songs from the data_df that is most dissimilar to 
            the average of the user's audio features as determined by NearestNeighbors.
    """

    features_df=normalize_data(features_df).values
    data_df = normalize_data(data_df)

    # Take average of features_df to form the user's average profile
    user_avg = features_df.mean(axis=0).reshape(1,-1)

    # Get data_df features with which to find nearest neighbors of user_avg
    samples = data_df[FEATURE_NAMES].values

    neigh=NearestNeighbors(n_neighbors=len(data_df))
    neigh.fit(samples)

    # Get the 10 most dissimilar songs
    bottom_ten_recs = neigh.kneighbors(user_avg, return_distance=False).flatten()[-10:]

    # Return song names of those bottom_ten_recs
    rec_names = [data_df.iloc[rec]["name"] for rec in bottom_ten_recs]
    return rec_names



if __name__ == "__main__":
    genius=lyricsgenius.Genius(GENIUS_ACCESS_TOKEN)
    # artist = genius.search_artist("Britney Spears", max_songs=0)
    # song=artist.song("Toxic")
    # print(song.lyrics)

    def get_lyrics(artists, songs):
        lyrics = [genius.search_song(song, artist).lyrics for (song, artist) in zip(songs, artists)]
        return lyrics
    ARTISTS = ["Lana Del Rey", "Bahamas", "Five Finger Death Punch", "Green Day"]
    SONGS = ["Salvatore", "No Depression", "Wrong Side of Heaven", "Boulevard of Broken Dreams"]

    lyrics = get_lyrics(ARTISTS, SONGS)
    print(lyrics)

           
