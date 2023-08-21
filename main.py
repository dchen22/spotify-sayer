import pandas as pd
import requests
import spotipy
from speech_recognition import Microphone, Recognizer, UnknownValueError
import spotipy as sp
from spotipy.oauth2 import SpotifyOAuth
import socket

from pepper import *

"""
To run this script, you must have a file in this directory called 'setup.txt'
In this file, enter all of the values of the required variables in the following format:

client_id=XXXXXXXX
client_secret=XXXXXXX
device_name=Jake's iMac
redirect_uri=https://example.com/callback/
username=jakeg135
scope=user-read-private user-read-playback-state user-modify-playback-state
"""

# Set variables from setup.txt
setup = pd.read_csv('setup.txt', sep='=', index_col=0, header=None)
client_id = '51602889753b4cea82048248df3d0383'
client_secret = 'c66bbd5b90e848e992e8c432290b4605'
device_name = socket.gethostname()  # gets current device name
redirect_uri = 'https://example.com/asdf/'
scope = 'user-read-private user-read-playback-state user-modify-playback-state'
username = 'puggywuggy2'

# Connecting to the Spotify account
auth_manager = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    username=username)
spotify = sp.Spotify(auth_manager=auth_manager)

# Selecting device to play from
devices = spotify.devices()
deviceID = None
for d in devices['devices']:
    d['name'] = d['name'].replace('’', '\'')
    if d['name'] == device_name:
        deviceID = d['id']
        break

# Setup microphone and speech recognizer
r = Recognizer()
m = None
input_mic = 1  # Use whatever is your desired input
for i, microphone_name in enumerate(Microphone.list_microphone_names()):
    # print(i, microphone_name)
    if i == input_mic:
        m = Microphone(device_index=i)

while True:
    """
    Commands will be entered in the specific format explained here:
     - the first word will be one of: 'album', 'artist', 'play'
     - then the name of whatever item is wanted
    """
    print('start while loop')
    with m as source:
        r.adjust_for_ambient_noise(source=source, duration=1)  # added duration=1 because apparently faster idk
        print('Listening...')
        audio = r.listen(source=source, timeout=5, phrase_time_limit=5)

    print('finished adjusting')
    command = None
    # print(audio.get_raw_data().hex())
    try:
        command = r.recognize_google(audio_data=audio, language='en-US').lower()
        print('asdlkfjsdf')
    except UnknownValueError:
        print('unknwonevalue')
        continue
    print(command)
    words = command.split()

    single_word_commands = ['resume', 'pause', 'skip', 'previous', 'restart']
    single_word_commands = set(single_word_commands)
    if len(words) <= 1:
        if len(words) == 0 or words[0] not in single_word_commands:
            print('Could not understand. Try again')
            continue

    name = ' '.join(words[1:])
    try:
        if words[0] == 'album':
            uri = get_album_uri(spotify=spotify, name=name)
            play_album(spotify=spotify, device_id=deviceID, uri=uri)
        elif words[0] == 'artist':
            uri = get_artist_uri(spotify=spotify, name=name)
            play_artist(spotify=spotify, device_id=deviceID, uri=uri)
        elif words[0] == 'play':
            if 'obama' in words and len(words) > words.index('obama') + 1:
                artist_name = ' '.join(words[words.index('obama') + 1:])
                print('track:', ' '.join(words[1:words.index('obama')]))
                print('artist:', artist_name)
                uri = get_track_and_artist_uri(spotify=spotify, track_artist_name=' '.join(words[1:words.index('obama')]) + ' ' + artist_name)
                play_track(spotify=spotify, device_id=deviceID, uri=uri)
                print('no error')
            else:
                uri = get_track_uri(spotify=spotify, name=name)
                play_track(spotify=spotify, device_id=deviceID, uri=uri)
        elif words[0] == 'playlist':
            uri = get_playlist_uri(spotify=spotify, name=name)
            play_album(spotify=spotify, device_id=deviceID, uri=uri)
        elif words[0] == 'find':
            pass
        elif words[0] == 'shuffle':
            if name == 'true' or name == 'on':
                spotify.shuffle(state=True, device_id=deviceID)
            elif name == 'false' or name == 'off':
                spotify.shuffle(state=False, device_id=deviceID)
            else:
                print('Did you mean "shuffle on/off"?')
        elif words[0] == 'resume':
            try:
                spotify.start_playback(device_id=deviceID)
            except (spotipy.SpotifyException, requests.HTTPError) as e:
                print('Error - playback may already be playing')
        elif words[0] == 'pause':
            try:
                spotify.pause_playback(device_id=deviceID)
            except (spotipy.SpotifyException, requests.HTTPError) as e:
                print('Error - playback may already be paused')
        elif words[0] == 'skip':
            spotify.next_track(device_id=deviceID)
        elif words[0] == 'previous':
            spotify.previous_track(device_id=deviceID)
        elif words[0] == 'restart':
            spotify.seek_track(position_ms=0)
        elif words[0] == 'volume':
            current_playback = spotify.current_playback()
            current_volume = current_playback['device']['volume_percent']
            d_volume = 10  # how much we're changing by
            if name == 'up':
                if current_volume <= 100 - d_volume:
                    spotify.volume(current_volume + d_volume, device_id=deviceID)
                else:
                    spotify.volume(100, device_id=deviceID)
            elif name == 'down':
                if current_volume >= d_volume:
                    spotify.volume(current_volume - d_volume, device_id=deviceID)
                else:
                    spotify.volume(0, device_id=deviceID)

    except InvalidSearchError:
        print('InvalidSearchError. Try Again')