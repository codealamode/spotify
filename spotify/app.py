import time
import pandas as pd
import secrets
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from flask import Flask, render_template, request, redirect, session
from .utils import *


# load_dotenv()
# SCOPE="user-library-read"
# SPOTIPY_CLIENT_ID=getenv("SPOTIPY_CLIENT_ID")
# SPOTIPY_CLIENT_SECRET=getenv("SPOTIPY_CLIENT_SECRET")
# SPOTIPY_REDIRECT_URI=getenv("SPOTIPY_REDIRECT_URI")


def create_app():

    app = Flask(__name__)
    app.secret_key=secrets.token_bytes(16)


    @app.route('/')
    def index():
        session["token_info"], authorized = get_token(session)

        return render_template('index.html', authorized=authorized)


    @app.route("/spotify_login")
    def authorization():
        sp = create_spotify_oauth()
        auth_url = sp.get_authorize_url()
        return redirect(auth_url)


    @app.route("/callback")
    def callback():
        sp = create_spotify_oauth()
        session.clear()
        code = request.args.get('code')
        token_info = sp.get_access_token(code, check_cache=False)
        
        session["token_info"] = token_info
        return redirect('/')
        #return session["token_info"]


    @app.route("/user_playlists")
    def user_playlists():
        sp = get_sp(session)        
        user_playlists = sp.current_user_playlists()["items"]

        return render_template("user_playlists.html", user_playlists = user_playlists)


    @app.route("/user_top_tracks")
    def user_top_tracks():
        sp = get_sp(session)

        #Get top 10 of user's recently listened to tracks
        user_top_tracks = sp.current_user_top_tracks(limit=20, time_range="short_term")["items"]
    
        #Get track ids for each track in user_top_tracks. Track id is needed to retrieve audio features for each of those tracks.
        top_track_ids =[track["id"] for track in sp.current_user_top_tracks(limit=10, time_range="short_term")["items"]]
        top_track_features = sp.audio_features(top_track_ids)

        #Create features dataframe and drop all unnecessary features
        features_df = pd.DataFrame(top_track_features).drop(columns=["type", "id", "uri", "track_href", "analysis_url"])

        #Write the df to a csv file
        features_df.to_csv("features_df.csv", index=False)

        #Get list of artist names for each track in user_top_tracks. 
        #Some tracks have multiple artists. In those cases, we choose just the first one to feed into get_lyrics()
        top_track_artists = [track["artists"][0]["name"] for track in user_top_tracks]

        #Get list of track names for each track in user_top_tracks
        top_track_names = [track["name"] for track in user_top_tracks]

        #list of lyrics for user's top tracks
        lyrics = get_lyrics([top_track_artists[3]], [top_track_names[3]])

        return render_template("user_top_tracks.html", top_track_artists=top_track_artists, top_track_names=top_track_names, lyrics=lyrics)
        

    return app

