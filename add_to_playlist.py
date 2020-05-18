import re
from pathlib import Path
import csv
import unidecode
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy import util

import my_util
import config as conf

with open(conf.CREDS_FILE_PATH, 'r', encoding='utf-8') as file:
    creds = file.readlines()
    cid = creds[0].strip()
    secret = creds[1]
    username = creds[2]
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
scope = 'playlist-modify-private playlist-read-private'
token = util.prompt_for_user_token(username, scope, client_id=cid, client_secret=secret,
                                   redirect_uri='http://localhost:8080')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager, auth=token)
user = sp.current_user()
user_id = user['id']

current_playlists = sp.current_user_playlists()
playlist_id = my_util.get_playlist_id(current_playlists=current_playlists, playlist_name=conf.PLAYLIST_NAME)
if not playlist_id:
    playlist_id = sp.user_playlist_create(user=user_id, name=conf.PLAYLIST_NAME, public=False)['id']

current_path = Path(__file__).parent.absolute()
with open(f'{current_path}/track_lists/{conf.TRACKLIST}', 'r', encoding='utf-8') as file:
    reader = csv.reader(file, delimiter=",")
    track_list = [row for row in reader]

tracks_found = []
missing_tracks = []
for entry in track_list:
    search_string = ' '.join(entry).replace('|', ' ')
    expected_artists = entry[0].split('|') + entry[2].split('|') if entry[2] else entry[0].split('|')
    search_results = sp.search(q=search_string, type='track')
    all_there = False
    artists = None
    track_titles = [track['name'] for track in search_results['tracks']['items']]
    for track in search_results['tracks']['items']:
        # check if all expected artists are in the track:
        artists = ' '.join(artist['name'] for artist in track['artists'])
        re_clean = re.compile(r'[()&,]|feat\.?|([rR]e)?[Mm]ix|[eE]xtended|[oO]riginal')
        re_space = re.compile(r'\s{2,}')
        artists_clean = re_clean.sub('', artists)
        artists_white = re_space.sub(' ', artists_clean)
        # artists_white = artists_white.replace('ï', 'i').replace('Ø', 'o').replace('ö', 'o')
        artists_normal = unidecode.unidecode(artists_white)
        expected_normal = [unidecode.unidecode(i) for i in expected_artists]
        expected_lower_str = '|'.join([i.lower() for i in expected_artists])
        all_there = all([i.lower() in artists_normal.lower() for i in expected_normal])
        if all_there:
            tracks_found.append(track['id'])
            break
    if not all_there:
        print(('entry:', entry), ('expected:', expected_artists), ('artists', artists), sep='::')
        print(search_results)
        missing_tracks.append('\n'.join([
            'Entry:' + '>'.join(entry),
            'Search:' + search_string,
            'Tracks:' + '\n\t'.join(track_titles),
            'Expected Artists:' + '|'.join(expected_artists),
            f'Found Artists:{artists}',
            f'Normalized: {expected_lower_str} in {artists_normal.lower()}', '\n']))

with open(f'{current_path}/results/{conf.PLAYLIST_NAME}', 'w', encoding='utf-8') as file:
    file.writelines(missing_tracks)

my_util.update_playlist(playlist_id=playlist_id, user_id=user_id, tracks=tracks_found, sp=sp)

