from spotipy import Spotify


def get_playlist_id(current_playlists, playlist_name):
    for playlist in current_playlists['items']:
        if playlist_name == playlist['name']:
            return playlist['id']
    return False


def update_playlist(playlist_id, user_id, tracks, sp: Spotify):
    playlist_record = sp.playlist(playlist_id=playlist_id)
    existing_ids = [i['track']['id'] for i in playlist_record['tracks']['items']]
    update_tracks = [track_id for track_id in tracks if track_id not in existing_ids]
    sp.user_playlist_add_tracks(user=user_id, playlist_id=playlist_id, tracks=update_tracks)