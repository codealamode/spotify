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
from spotify.dummy_data import user_top_tracks as DEBUG_FILLER

# TODO:
# > Add "is_logged_in" check to block routes if a user isn't logged in yet.
# > Make imports smaller at end of project by only importing dependencies.

big_data = pd.read_csv("../spotify/data/data.csv").drop(columns=["explicit", 
                                                                 "year", 
                                                                 "release_date"])


def create_app():

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
        code = request.args.get('code')
        token_info = sp.get_access_token(code, check_cache=False)
        
        session["token_info"] = token_info

        return redirect(url_for("main_app"))


    @app.route("/app", methods=["GET", "POST"])
    def main_app():
        sp = get_sp(session)

        # Login check/redirect.
        session["token_info"], authorized = get_token(session)
        if not authorized:
            return redirect(url_for("index"))

        # The only POST request possible to this page is if the main app
        # "Generate Predictions" button is clicked.
        if request.method == 'GET':     
            return render_template('main_app.html', sp=sp, songs=[])

        # Pull user top tracks from spotify API.
        user_top_tracks = sp.current_user_top_tracks(limit=10, 
                                                     time_range="short_term"
                                                    )["items"]
        # Raise error if no recent top tracks.
        if not user_top_tracks:
            return render_template("error.html", type='Empty Spotify')

        # Pull top track audio features.
        top_track_ids =[track["id"] for track in user_top_tracks]
        top_track_features = sp.audio_features(top_track_ids)

        # Cast features to a dataframe.
        cols = ["type", "id", "uri", "track_href", "analysis_url", 
                "time_signature"]
        top_df = pd.DataFrame(top_track_features).drop(columns=cols)

        # Write the df to a csv file !!!!!!!!!!!!!!!!!!!!!!HACK!!!!!!!!!!!!!!!!!
        top_df.to_csv("top_df.csv", index=False)


        top_track_artists = [track["artists"][0]["name"] for track in 
                             user_top_tracks]
        top_track_names = [track["name"] for track in user_top_tracks]

        # Pull from the users form to check if they unchecked the bad 
        # recommendation check box
        wants_good_recommendations = request.form.get('goodorbad')
        if wants_good_recommendations:
            rec_names, rec_ids, rec_artists = recommend(top_df, big_data,
                                                        bad=False)

            rec_links = song_links(rec_ids)

            rec_lyrics = get_lyrics(rec_artists, rec_names)
            noun_chunks = generate_noun_chunks(rec_lyrics)
            playlist_name = choose_name(noun_chunks)

        else:
            rec_names, rec_ids, rec_artists = recommend(top_df, big_data)

            rec_links = song_links(rec_ids)

            rec_lyrics = get_lyrics(rec_artists, rec_names)
            noun_chunks = generate_noun_chunks(rec_lyrics)
            playlist_name = choose_name(noun_chunks)



        songs = [uri.split(':')[-1] for uri in rec_links]
        # songs = [song['uri'].split(':')[-1] for song in DEBUG_FILLER]
        print(songs)
        print(rec_links)
        return render_template('main_app.html', sp=sp, songs=songs, title=playlist_name)


    @app.route("/user_playlists")
    def user_playlists():
        sp = get_sp(session)
        # !BUG! A bug happens here if a user tries to access this route without
        #       being logged in...
        user_playlists = sp.current_user_playlists()["items"]

        return render_template("user_playlists.html", 
                                user_playlists = user_playlists, 
                                title="Playlists")


    @app.route("/user_top_tracks")
    def user_top_tracks():
        sp = get_sp(session)

        # Get top 10 of user's recently listened to tracks
        # !BUG! A bug happens here if a user tries to access this route without
        #       being logged in...
        user_top_tracks = sp.current_user_top_tracks(limit=10, 
                                                     time_range="short_term"
                                                     )["items"]

        #############
        # Get track ids for each track in user_top_tracks. Track id is needed 
        # to retrieve audio features for each of those tracks.
        top_track_ids =[track["id"] for track in user_top_tracks]
        top_track_features = sp.audio_features(top_track_ids)

        # Create features dataframe and drop all unnecessary features
        try:
            cols = ["type", "id", "uri", "track_href", "analysis_url", "time_signature"]
            features_df = pd.DataFrame(top_track_features).drop(columns=cols)
        except:
            return render_template("error.html",
                                   type='0 - Empty Spotify')

        # Write the df to a csv file
        features_df.to_csv("features_df.csv", index=False)

        # Get list of artist names for each track in user_top_tracks. 
        # NOBUG: Some tracks have multiple artists. In those cases, we choose 
        #        just the first one to feed into get_lyrics()
        top_track_artists = [track["artists"][0]["name"] for track in user_top_tracks]

        # Get list of track names for each track in user_top_tracks
        top_track_names = [track["name"] for track in user_top_tracks]

        # list of lyrics for user's top tracks
        # NOTE: takes around 20 seconds to pull lyrics for 10 tracks
        #lyrics = get_lyrics(top_track_artists, top_track_names)

        # Read from song dataset
        data_df = pd.read_csv("../spotify/data/data.csv").drop(columns=["explicit", "year", "release_date"])
        
        # Get bad recommendations
        rec_names, rec_ids, rec_artists = recommend(features_df, data_df)

        # Get links to spotify page of the bad recommendations
        rec_links = song_links(rec_ids)

        #names_links = zip(rec_names, rec_links)
        rec_lyrics = get_lyrics(rec_artists, rec_names)
        noun_chunks = generate_noun_chunks(rec_lyrics)
        playlist_name = choose_name(noun_chunks)
        return render_template("user_top_tracks.html", 
                                top_track_names=top_track_names, 
                                rec_names=rec_names,
                                playlist_name=playlist_name,
                                title="Top Tracks")


    return app
