from flask import Flask, request, redirect, session, render_template,jsonify
import requests
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
import speech_recognition as sr
import json
import os
import threading

app = Flask(__name__)

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
REDIRECT_URI = 'http://localhost:3000/callback' # your redirect URI
CLIENT_ID = "ADD YOUR CLIENT ID"
CLIENT_SECRET = "ADD YOUR SECRET"
SCOPE = ' '.join([
    "user-read-playback-state",
    "app-remote-control",
    "user-modify-playback-state",
    "playlist-read-private",
    "playlist-read-collaborative",
    "user-read-currently-playing",
    "user-library-modify",
    "playlist-modify-private",
    "playlist-modify-public"
])
KEYWORDS_FILE = 'keywords.json'

# Helper Functions
def get_headers(token):
    return {"Authorization": "Bearer " + token}

def load_keywords():
    try:
        with open(KEYWORDS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_keywords(keywords):
    with open(KEYWORDS_FILE, 'w') as file:
        json.dump(keywords, file, indent=4)

# Routes
@app.route("/login")
def login():
    spotify = OAuth2Session(CLIENT_ID, scope=SCOPE, redirect_uri=REDIRECT_URI)
    authorization_url, state = spotify.authorization_url(AUTH_URL)
    return redirect(authorization_url)

@app.route("/callback", methods=['GET'])
def callback():
    code = request.args.get('code')
    spotify = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI)
    token = spotify.fetch_token(TOKEN_URL, client_secret=CLIENT_SECRET, code=code)

    session['access_token'] = token['access_token']  # Store access token in session
    session['keywords'] = load_keywords()  # Load keywords
    return redirect("/listen")

@app.route("/listen")
def listen():
    access_token = session.get('access_token')
    raw_keywords = session.get('keywords', {})
    headers = get_headers(access_token)

    # Normalize and prepare keywords: strip any prefix and convert to lowercase
    keywords = {v.lower(): k.split('-')[1] for k, v in raw_keywords.items() if v and v.strip()}

    print("Active keywords and their associated playlists:")
    for command, playlist_id in keywords.items():
        print(f"{command}: {playlist_id}")

    # Start the listening thread with the normalized keywords
    listener_thread = threading.Thread(target=continuous_listen, args=(access_token, keywords, headers))
    listener_thread.start()

    return jsonify({"message": "Listening service started"}), 200

def continuous_listen(access_token, keywords, headers):
    recognizer = sr.Recognizer()
    microphone = sr.Microphone(device_index=1)

    while True:
        try:
            with microphone as source:
                print("Listening for commands...")
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)
                command = recognizer.recognize_google(audio).lower().strip()  # Normalize the command

                if command in keywords:
                    playlist_id = keywords[command]
                    print(f"Command '{command}' recognized, associated with playlist ID {playlist_id}.")
                    response = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers=headers)
                    if response.status_code == 200 and 'item' in response.json() and 'uri' in response.json()['item']:
                        song_uri = response.json()['item']['uri']
                        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
                        params = {'uris': [song_uri]}
                        result = requests.post(url, json=params, headers=headers)
                        if result.status_code == 201:
                            print(f"Added song to playlist: {playlist_id}")
                        else:
                            print(f"Failed to add song: {result.status_code} {result.text}")
                    else:
                        print("No song is currently playing or failed to fetch song.")
                else:
                    print(f"Keyword '{command}' not recognized.")
        except (sr.RequestError, sr.UnknownValueError) as e:
            print(f"Error recognizing speech: {str(e)}")



@app.route('/playlists', methods=['GET', 'POST'])
def playlists():
    if request.method == 'POST':
        # Extract keywords and save them in the format {playlist_id: keyword}
        keywords = {key.split('-')[1]: request.form[key] for key in request.form if key.startswith('keyword-')}
        save_keywords(keywords)
        return redirect('/playlists')

    # GET request: Fetch and display playlists
    access_token = session.get('access_token')
    headers = get_headers(access_token)
    response = requests.get("https://api.spotify.com/v1/me/playlists", headers=headers)
    playlists = response.json().get('items', [])

    # Load existing keywords
    existing_keywords = load_keywords()

    # Map keywords back to their playlists
    keywords_for_playlists = {playlist['id']: existing_keywords.get(playlist['id'], '') for playlist in playlists}

    return render_template('playlists.html', playlists=playlists, keywords=keywords_for_playlists)

def load_keywords():
    try:
        with open(KEYWORDS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_keywords(keywords):
    with open(KEYWORDS_FILE, 'w') as file:
        json.dump(keywords, file, indent=4)

if __name__ == '__main__':
    app.secret_key = '1234'  # Use a secure, unique secret key!
    app.run(port=3000, debug=True)