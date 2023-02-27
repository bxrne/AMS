# Flask server to render templates, oracle sql db conn and get/post for simple shit

from flask import Flask, render_template, request, redirect, url_for


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')