import time
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

    # Home
    @app.route('/')
    def index():
        # Pulls login status to pass into renderer.
        session["token_info"], authorized = get_token(session)

        return render_template('index.html', 
                               session_token = session.get("token_info", ""), 
                               authorized=authorized)

    # Redirects users to login with spotify.
    @app.route("/spotify_login")
    def authorization():
        sp = create_spotify_oauth()
        auth_url = sp.get_authorize_url()

        return redirect(auth_url)

    # Welcomes users back from spotify login.
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

        return render_template("user_playlists.html",
                               user_playlists = user_playlists)
    
    @app.route("/user_top_tracks")
    def user_top_tracks():
        sp = get_sp(session)
        user_top_tracks = sp.current_user_top_tracks(limit=20, 
                                                     time_range="short_term",
                                                     )["items"]
        return render_template("user_top_tracks.html", 
                               user_top_tracks=user_top_tracks)

    @app.route("/user_profile")
    def user_profile():
        """This is for getting all the tracks for each of the user's playlists. 
            NOTE: still a work in progress."""
        playlist_ids=[]
        sp = get_sp(session)
        user_id = sp.current_user()["id"]
        user_playlists = sp.user_playlists(user=user_id)["items"]
        playlist_ids = [playlist["id"] for playlist in user_playlists]

        aa = sp.user_playlist_tracks(user=user_id, 
                                     playlist_id=playlist_ids[1])["items"]
        return str(aa)

    return app