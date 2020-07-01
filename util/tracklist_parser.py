from pathlib import Path
import csv
import config as conf

current_path = Path(__file__).parent.absolute()
with open(f'{current_path}/track_lists/{conf.TRACKLIST}', 'r', encoding='utf-8') as file:
    reader = csv.reader(file, delimiter=",")
    track_list = [row for row in reader]