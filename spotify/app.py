# Built-in
import time
import secrets

# Third party
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from flask import Flask, render_template, request, redirect, session, url_for

# Local
from spotify.utils import *

# TODO:
# > Make imports smaller at end of project by only importing dependencies.

big_data = pd.read_csv("../spotify/data/data.csv").drop(columns=["explicit", 
                                                                 "year", 
                                                                 "release_date"])

app = Flask(__name__)
app.secret_key=secrets.token_bytes(16)

# Home
@app.route("/")
def index():
    # Pulls login status to pass into renderer.
    session["token_info"], authorized = get_token(session)
    
    # Keep the user on this page if not authorized otherwise direct to app.
    if not authorized:
        return render_template("index.html")
    else:
        return redirect(url_for("main_app"))


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
    code = request.args.get("code")
    token_info = sp.get_access_token(code, check_cache=False)
    
    session["token_info"] = token_info

    return redirect(url_for("main_app"))


@app.route("/app", methods=["GET", "POST"])
def main_app():
    sp = get_sp(session)  # Spotify API connection.

    # Login check/redirect.
    session["token_info"], authorized = get_token(session)
    if not authorized:
        return redirect(url_for("index"))

    # The only POST request possible to this page is if the main app
    # "Generate Predictions" button is clicked.
    if request.method == "GET":     
        return render_template("main_app.html", sp=sp, songs=[])

    # Pull user top tracks from spotify API.
    user_top_tracks = sp.current_user_top_tracks(limit=10, 
                                                    time_range="short_term"
                                                )["items"]
    # Raise error if no recent top tracks.
    if not user_top_tracks:
        return render_template("error.html", type="Empty Spotify")

    # Pull top track audio features.
    top_track_ids =[track["id"] for track in user_top_tracks]
    top_track_features = sp.audio_features(top_track_ids)

    # Cast features to a dataframe.
    cols = ["type", "id", "uri", "track_href", "analysis_url", 
            "time_signature"]
    top_df = pd.DataFrame(top_track_features).drop(columns=cols)

    # For good recommendations
    if "goodrecs" in request.form:
        # Force at least one song to have lyrics. 
        rec_lyrics = None
        while rec_lyrics is None:
            rec_names, rec_ids, rec_artists = recommend(top_df, big_data,
                                                        bad=False)
            rec_lyrics = get_lyrics(rec_artists, rec_names)

        noun_chunks = generate_noun_chunks(rec_lyrics)
        playlist_name = choose_name(noun_chunks)

    # For bad recommendation.
    elif "badrecs" in request.form:
        rec_lyrics = None
        while rec_lyrics is None:
            rec_names, rec_ids, rec_artists = recommend(top_df, big_data)
            rec_lyrics = get_lyrics(rec_artists, rec_names)

        noun_chunks = generate_noun_chunks(rec_lyrics)
        playlist_name = choose_name(noun_chunks)

    # Pull and clean URI for embedding each song. 
    rec_links = song_links(rec_ids)
    songs = [uri.split(":")[-1] for uri in rec_links]
    return render_template("main_app.html", sp=sp, songs=songs, 
                            title=playlist_name)


@app.route("/team")
def team():
    return render_template("team.html")


@app.route("/about")
def about():
    return render_template("about.html")