import re
from pathlib import Path

import requests
from lxml import html
import config as conf

base_url = 'https://www.beatport.com'

genre = conf.GENRE
endpoint = f'{base_url}/genre{genre}/top-100'

page = requests.get(url=endpoint)
tree = html.fromstring(page.content)

# combine all artists, '|' separated
artist_elements = tree.xpath('//li[@class="bucket-item ec-item track"]//p[@class="buk-track-artists"]')
artist_combined = []
for entry in artist_elements:
    artist_combined.append('|'.join([i.text for i in entry.xpath('.//a')]))
re_clean = re.compile(r'[()&,]|feat\.?|([rR]e)?[Mm]ix|[eE]xtended|[oO]riginal')
re_space = re.compile(r'\s{2,}')
artists = [re_space.sub(' ', j) for j in [re_clean.sub('', i) for i in artist_combined]]

# combine remix artists, '|' separated
remixer_elements = tree.xpath('//li[@class="bucket-item ec-item track"]//p[@class="buk-track-remixers"]')
remixers_combined = []
for entry in remixer_elements:
    remixers_combined.append('|'.join([i.text for i in entry.xpath('.//a')]))
remixers = [re_space.sub(' ', j) for j in [re_clean.sub('', i) for i in remixers_combined]]

track_elements = tree.xpath('//li[@class="bucket-item ec-item track"]//span[@class="buk-track-primary-title"]')
track_titles = [re_space.sub(' ', j) for j in [re_clean.sub('', i.text) for i in track_elements]]

current_path = Path(__file__).parent.absolute()
with open(f'{current_path}/track_lists/top_100_bp.txt', 'w', encoding='utf-8') as file:
    artist_track_list = zip(artists, track_titles, remixers)
    [file.write(','.join(i).rstrip() + '\n') for i in artist_track_list]
