import pandas as pd
from speech_recognition import Microphone, Recognizer, UnknownValueError
import spotipy as sp
from spotipy.oauth2 import SpotifyOAuth

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
setup = pd.read_csv('/spotify-sayer2/setup.txt', sep='=', index_col=0, header=None)
client_id = '51602889753b4cea82048248df3d0383'
client_secret = 'c66bbd5b90e848e992e8c432290b4605'
device_name = 'conputer'
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
    print('asdf')
    with m as source:
        r.adjust_for_ambient_noise(source=source)
        audio = r.listen(source=source)

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
    # words = ['play', 'bohemian', 'rhapsody']
    if len(words) <= 1:
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
        else:
            print('Specify either "album", "artist" or "play". Try Again')
    except InvalidSearchError:
        print('InvalidSearchError. Try Again')