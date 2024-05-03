
# Spotify Voice Recognition Project

This project enables voice-controlled interactions with Spotify, allowing users to add songs to their playlists using spoken commands. Built with Flask and integrating the Spotify Web API, it offers a seamless experience for managing playlists through voice.

## Features

- **Voice Commands**: Use your voice to control Spotify playback and manage playlists.
- **Playlist Management**: Add the currently playing song to a designated playlist through voice.
- **Continuous Listening**: The app continuously listens for commands, making it easy to use while away from your keyboard.
- **Secure Authentication**: Implements OAuth2 for secure authentication with Spotify.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

What things you need to install the software and how to install them:

```bash
pip install Flask SpeechRecognition requests_oauthlib
```

### Installing

A step-by-step series of examples that tell you how to get a development environment running:

#### Clone the repository

```bash
git clone https://github.com/yourusername/spotify-voice-recognition.git
cd spotify-voice-recognition
```

#### Set up your Spotify Developer Account

- Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/) and create an app.
- Note down the Client ID and Client Secret.
- Set the Redirect URI to `http://localhost:3000/callback`.
- Place your Client ID and Client Secret into the `.env` file in your project directory. Create this file if it doesn't exist and add the following:

```plaintext
SPOTIFY_CLIENT_ID='your_spotify_client_id_here'
SPOTIFY_CLIENT_SECRET='your_spotify_client_secret_here'
```

#### Run the application

```bash
python spotify_playlist.py
```

#### Navigate the application

- **Login Page**: Open your browser and visit `http://localhost:3000`. Start by logging in using your Spotify credentials.
- **Listening Page**: After logging in, you will be directed to start interacting with your voice. Simply speak the playlist names to add the currently playing song.

## Usage

To use the application, speak the name of the playlist you want to add the current song to after pressing the listen button. The application listens and responds to the following commands:

- "Add to Roadtrip": Adds the current song to your 'Roadtrip' playlist.
- "Add to Gym": Adds the current song to your 'Gym' playlist.

## Built With

- [Flask](http://flask.pocoo.org/) - The web framework used
- [Spotify Web API](https://developer.spotify.com/documentation/web-api/) - Used to control Spotify playback and manage playlists
- [Python SpeechRecognition](https://pypi.org/project/SpeechRecognition/) - Library for performing speech recognition

