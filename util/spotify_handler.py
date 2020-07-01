import re

import spotipy
import unidecode
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy import util
from spotipy.exceptions import SpotifyException

import config as conf


class SpotipyHandler:
    # TODO: This is temporary for local development:
    with open(conf.CREDS_FILE_PATH, 'r', encoding='utf-8') as file:
        creds = file.readlines()
        cid = creds[0].strip()
        secret = creds[1].strip()
        username = creds[2]

    def __init__(self, username=username, cid=cid, secret=secret):
        client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
        scope = 'playlist-modify-private playlist-read-private'  # playlist-read-public playlist-modify-public
        token = util.prompt_for_user_token(username=username, scope=scope, client_id=cid, client_secret=secret,
                                           redirect_uri='http://localhost:8080')
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager, auth=token)
        self.user = self.sp.current_user()
        self.user_id = self.user['id']
        self.current_playlists = self.get_playlists()

    def get_playlists(self):
        all_playlists = []
        playlist_results = self.sp.current_user_playlists()
        offset = 0
        while playlist_results['items']:
            all_playlists.extend(playlist_results['items'])
            offset += 50
            playlist_results = self.sp.current_user_playlists(offset=offset)
        return all_playlists

    def get_playlist_id_by_name(self, playlist_name):
        for playlist in self.current_playlists:
            if playlist_name == playlist['name']:
                return playlist['id']
        return False

    def create_playlist(self, playlist_name):
        playlist_id = self.sp.user_playlist_create(user=self.user_id, name=playlist_name, public=False)['id']
        return playlist_id

    def get_track_lists(self, track_list):
        tracks_found = []
        missing_tracks = []
        for entry in track_list:
            search_string = ' '.join(entry['artists']) + ' ' + entry['track_title'] + ' ' + ' '.join(entry['remixers'])
            expected_artists = entry['artists']
            search_results = self.sp.search(q=search_string, type='track')
            all_there = False
            artists = None
            track_titles = [track['name'] for track in search_results['tracks']['items']]
            artists_normal = ''
            expected_lower_str = ''
            for track in search_results['tracks']['items']:
                # check if all expected artists are in the track:
                artists = ' '.join(artist['name'] for artist in track['artists'])
                re_clean = re.compile(r'[()&,]|feat\.?|([rR]e)?[Mm]ix|[eE]xtended|[oO]riginal')
                re_space = re.compile(r'\s{2,}')
                artists_clean = re_clean.sub('', artists)
                artists_white = re_space.sub(' ', artists_clean)
                # TODO: implement text match rules for special characters
                # artists_white = artists_white.replace('ï', 'i').replace('Ø', 'o').replace('ö', 'o')
                artists_normal = unidecode.unidecode(artists_white)
                expected_normal = [unidecode.unidecode(i) for i in expected_artists]
                expected_lower_str = ' '.join([i.lower() for i in expected_artists])
                all_there = all([i.lower() in artists_normal.lower() for i in expected_normal])
                if all_there:
                    tracks_found.append(track)
                    break
            if not all_there:
                entry.update({
                    'Search': search_string,
                    'Tracks': track_titles,
                    'Expected Artists': expected_artists,
                    'Found Artists': artists,
                    'expected vs. found': (expected_lower_str, artists_normal.lower()),
                    'Normalized Match': expected_lower_str in artists_normal.lower()
                })
                missing_tracks.append(entry)
        return tracks_found, missing_tracks

    def update_playlist(self, playlist_id, track_id_list):
        try:
            playlist_tracks = self.get_tracks_by_playlist_id(playlist_id=playlist_id)
            existing_ids = [i['track']['id'] for i in playlist_tracks]
            update_tracks = [track_id for track_id in track_id_list if track_id not in existing_ids]
            if update_tracks:
                self.sp.user_playlist_add_tracks(user=self.user_id, playlist_id=playlist_id, tracks=update_tracks)
        except SpotifyException as e:
            print('haha')
            raise e

    def playlist_list_by_track(self, track_id):
        """ returns a list of playlist names the track is found in """
        pass

    def get_tracks_by_playlist_id(self, playlist_id):
        all_tracks = []
        playlist_results = self.sp.playlist_tracks(playlist_id=playlist_id)
        offset = 0
        while playlist_results['items']:
            all_tracks.extend(playlist_results['items'])
            offset += 100
            playlist_results = self.sp.playlist_tracks(playlist_id=playlist_id, offset=offset)
        return all_tracks

    def get_tracks_by_playlist_name(self, playlist_name):
        playlist_id = self.get_playlist_id_by_name(playlist_name=playlist_name)
        return self.get_tracks_by_playlist_id(playlist_id=playlist_id)
