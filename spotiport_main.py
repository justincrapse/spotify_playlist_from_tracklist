import datetime

from util.spotify_handler import SpotipyHandler
from util.mongo_db_handler import MDBConnection
from scrapers import beatport_scraper

now = datetime.datetime.now()
day, month, year = now.day, now.month, now.year

date = f'{year}-{month}-{day}'

my_sp = SpotipyHandler()
mdb = MDBConnection()

new_track_payload = {
    'source': 'beatport',
    'artists': None,
    'track_title': None,
    'remixers': None,
    'genre': None,
    'spotify_track_id': None,
    'spotify_availability': {'available': True, 'first_search_date': date, 'first_available_date': None},
    'in_playlists': None
}

existing_spotify_track_id_list = mdb.get_all_spotify_ids()


def run_daily_update():
    for key, value in beatport_scraper.bp_genre_dict.items():
        top_100_dict_list = beatport_scraper.get_top_100_playlist(genre_url_snippet=value)
        playlist_name = f'BP_TOP_100_{key}_{month}_{year}'
        playlist_id = my_sp.get_playlist_id_by_name(playlist_name=playlist_name)
        if not playlist_id:
            playlist_id = my_sp.create_playlist(playlist_name=playlist_name)
        tracks_found, missing_tracks = my_sp.get_track_lists(track_list=top_100_dict_list)
        track_ids_to_add = [track['id'] for track in tracks_found if track['id'] not in existing_spotify_track_id_list]
        if track_ids_to_add:
            my_sp.update_playlist(playlist_id=playlist_id, track_id_list=track_ids_to_add)

        # update mega playlist (only if not in track database in mongodb)
        tracks_to_add = [track for track in tracks_found if track['id'] not in existing_spotify_track_id_list]
        track_ids_to_add = [track['id'] for track in tracks_to_add]
        playlist_name = '+++++BP_TOP_100(S)_MEGA+++++'
        playlist_id = my_sp.get_playlist_id_by_name(playlist_name=playlist_name)
        if not playlist_id:
            playlist_id = my_sp.create_playlist(playlist_name=playlist_name)['id']
        if track_ids_to_add:
            my_sp.update_playlist(playlist_id=playlist_id, track_id_list=track_ids_to_add)

        # record track successes and failures in mongodb
        document_list = []
        for track in tracks_to_add:
            document = {
                'source': 'beatport',
                'artists': None,
                'track_title': None,
                'remixers': None,
                'genre': None,
                'spotify_track_id': track['id'],
                'spotify_availability': {'available': True, 'first_search_date': date, 'first_available_date': None},
                'in_playlists': None,
                'spotify_track_info': track
            }
            document_list.append(document)
        if document_list:
            mdb.insert_many(document_list=document_list)


def update_database_with_playlist(playlist_name):
    playlist_tracks = my_sp.get_tracks_by_playlist_name(playlist_name=playlist_name)
    document_list = []
    for track in playlist_tracks:
        document = {
            'source': 'beatport',
            'artists': None,
            'track_title': None,
            'remixers': None,
            'genre': None,
            'spotify_track_id': track['track']['id'],
            'spotify_availability': {'available': True, 'first_search_date': date, 'first_available_date': None},
            'in_playlists': None,
            'spotify_track_info': track['track']
        }
        document_list.append(document)
    mdb.insert_many(document_list=document_list)


if __name__ == '__main__':
    # update_database_with_playlist(playlist_name='+++++BP_TOP_100(S)_MEGA+++++')
    run_daily_update()
