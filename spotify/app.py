from flask import Flask, render_template
from os import getenv
import os


def create_app():
    app = Flask(__name__)

    
    @app.route('/')
    def index():
        return render_template('index.html')


    return app
