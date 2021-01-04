import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from flask import Flask, render_template, redirect
from os import getenv
from dotenv import load_dotenv

load_dotenv()


SPOTIPY_CLIENT_ID=getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET=getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI=getenv("SPOTIPY_REDIRECT_URI")

def create_app():
    app = Flask(__name__)
    
    
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route("/spotify_login")
    def authorization():

        sp = SpotifyOAuth(scope="user-library-read")
        auth_url = sp.get_authorize_url()
        return redirect(auth_url)

    return app
