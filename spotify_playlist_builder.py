import datetime

from util.spotify_handler import SpotipyHandler
from util.mongo_db_handler import MDBConnection
from scrapers import beatport_scraper

now = datetime.datetime.now()


class SpotifyPlaylistBuilder:
    day, month, year = now.day, now.month, now.year
    date = f'{year}-{month}-{day}'
    
    def __init__(self):
        self.my_sp = SpotipyHandler()
        self.mdb = MDBConnection()
        self.existing_spotify_track_id_list = self.mdb.get_all_spotify_ids()
        self.tracks_found = None
        self.missing_tracks = None
        self.total_tracks_added_mega = 0

    def update_bp_playlist(self, genre, url):
        top_100_dict_list = beatport_scraper.get_top_100_playlist(genre_url_snippet=url)
        # playlist_name = f'BP_TOP_100_{genre}_{self.month}_{self.year}'
        # playlist_id = self.my_sp.get_playlist_id_by_name(playlist_name=playlist_name)
        # if not playlist_id:
        #     playlist_id = self.my_sp.create_playlist(playlist_name=playlist_name)
        tracks_found, missing_tracks = self.my_sp.get_track_lists(track_list=top_100_dict_list)
        tracks_to_add = [track for track in tracks_found if track['id'] not in self.existing_spotify_track_id_list]
        track_ids_to_add = [track['id'] for track in tracks_to_add]
        # if track_ids_to_add:
        #     self.my_sp.update_playlist(playlist_id=playlist_id, track_id_list=track_ids_to_add)
        #     print(f'{len(track_ids_to_add)} tracks added for {playlist_name} playlist')
        self.tracks_found, self.missing_tracks = tracks_found, missing_tracks

        # add to mongodb:
        document_list = []
        for track in tracks_to_add:
            document = {
                'source': 'beatport', 'artists': None, 'track_title': None, 'remixers': None,
                'genre': genre,
                'spotify_track_id': track['id'],
                'spotify_availability': {'found': True, '1st_search_date': self.date, '1st_available_date': None},
                'in_playlists': None,
                'spotify_track_info': track
            }
            document_list.append(document)
        if document_list:
            self.mdb.insert_many(document_list=document_list)

        # update mega lists
        self.update_mega_playlist()

    def update_mega_playlist(self):
        tracks_to_add = [track for track in self.tracks_found if track['id'] not in self.existing_spotify_track_id_list]
        track_ids_to_add = [track['id'] for track in tracks_to_add]
        playlist_name = '+++++BP_TOP_100(S)_MEGA+++++'
        playlist_id = self.my_sp.get_playlist_id_by_name(playlist_name=playlist_name)
        if not playlist_id:
            playlist_id = self.my_sp.create_playlist(playlist_name=playlist_name)['id']
        if track_ids_to_add:
            self.my_sp.update_playlist(playlist_id=playlist_id, track_id_list=track_ids_to_add)
            self.my_sp.update_playlist_by_name(playlist_name='BP MEGA BACKUP', track_id_list=track_ids_to_add)
            self.total_tracks_added_mega += len(track_ids_to_add)

    def run_daily_update(self):
        for key, value in beatport_scraper.bp_genre_dict.items():
            self.update_bp_playlist(genre=key, url=value)

            for track in self.missing_tracks:
                track.update({
                    'spotify_availability': {'found': False, '1st_search_date': self.date, '1st_available_date': None},
                    'genre': key
                })
            if self.missing_tracks:
                self.mdb.set_collection('missing_tracks')
                self.mdb.insert_one_by_list(document_list=self.missing_tracks)
                self.mdb.set_collection('track_entries')
            print(f'{key} update complete')
        print(f'{self.total_tracks_added_mega} Tracks added to Mega')

    def update_database_with_playlist(self, playlist_name):
        playlist_tracks = self.my_sp.get_tracks_by_playlist_name(playlist_name=playlist_name)
        document_list = []
        for track in playlist_tracks:
            document = {
                'source': 'beatport',
                'artists': None,
                'track_title': None,
                'remixers': None,
                'genre': None,
                'spotify_track_id': track['track']['id'],
                'spotify_availability': {'available': True, 'first_search_date': self.date, 'first_available_date': None},
                'in_playlists': None,
                'spotify_track_info': track['track']
            }
            document_list.append(document)
        self.mdb.insert_many(document_list=document_list)


if __name__ == '__main__':
    # update_database_with_playlist(playlist_name='+++++BP_TOP_100(S)_MEGA+++++')
    spb = SpotifyPlaylistBuilder()
    spb.run_daily_update()
