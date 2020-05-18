import datetime
now = datetime.datetime.now()
day, month, year = now.day, now.month, now.year

TRANCE = '/trance/7'
PSY_TRANCE = '/psy-trance/13'
BREAKS = '/breaks/9'
DOWNTEMPO = '/electronica-downtempo/3'

GENRE = DOWNTEMPO
GENRE_TEXT = GENRE.split('/')[1].upper()
TRACKLIST = 'top_100_bp.txt'
PLAYLIST_NAME = f'BP_TOP_100_{GENRE_TEXT}_{month}_{year}'

print(GENRE_TEXT)
print(PLAYLIST_NAME)
