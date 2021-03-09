import datetime
import re
from typing import List
import requests
from lxml import html

now = datetime.datetime.now()
day, month, year = now.day, now.month, now.year

from util.mongo_db_handler import MDBConnection

bp_genre_dict = dict(
    # TRANCE='/trance/7',
    BREAKS='/breaks/9',
    DOWNTEMPO='/organic-house-downtempo/93',
    DEEP_HOUSE='/deep-house/12',
    BASS_HOUSE='/bass-house/91',
    PROGRESSIVE_HOUSE='/progressive-house/15'
    # TOP='top'
)

base_url = 'https://www.beatport.com'
collection_name = 'bp_top_100_lists'

mdb = MDBConnection(collection_name=collection_name)

re_clean = re.compile(r'[()&,]|feat\.?|([rR]e)?[Mm]ix|[eE]xtended|[oO]riginal')
re_sp = re.compile(r'\s{2,}')


def get_top_100_playlist(genre_url_snippet) -> List[dict]:
    if genre_url_snippet == 'top':
        endpoint = f'{base_url}/top-100'
    else:
        endpoint = f'{base_url}/genre{genre_url_snippet}/top-100'
    cached_playlist = mdb.get_cached_playlist(genre_url=endpoint, date=f'{year}-{month}-{day}')
    if cached_playlist:
        return cached_playlist
    page = requests.get(url=endpoint)
    tree = html.fromstring(page.content)
    
    # parse artist[s]
    artist_elems = tree.xpath('//li[@class="bucket-item ec-item track"]//p[@class="buk-track-artists"]')
    artist_list = [[re_sp.sub(' ', re_clean.sub('', i.text)) for i in entry.xpath('.//a')] for entry in artist_elems]
    
    # parse remixer[s]
    remixer_elems = tree.xpath('//li[@class="bucket-item ec-item track"]//p[@class="buk-track-remixers"]')
    remixer_list = [[re_sp.sub(' ', re_clean.sub('', i.text)) for i in entry.xpath('.//a')] for entry in remixer_elems]
    
    # parse track titles
    track_elements = tree.xpath('//li[@class="bucket-item ec-item track"]//span[@class="buk-track-primary-title"]')
    track_list = [re_sp.sub(' ', re_clean.sub('', i.text)) for i in track_elements]

    return_list = []
    for artists, track_title, remixers in zip(artist_list, track_list, remixer_list):
        return_list.append(dict(artists=artists, track_title=track_title, remixers=remixers))

    # cache playlist in mdb for the day:
    mdb.cache_playlist(track_dict_list=return_list, genre_url=endpoint, date=f'{year}-{month}-{day}')

    # TODO: delete all older cached playlists?? Or maybe keep to datamine over time.
    return return_list


if __name__ == '__main__':
    result = get_top_100_playlist(genre_url_snippet=bp_genre_dict['TRANCE'])
    print(*result, sep='\n')
