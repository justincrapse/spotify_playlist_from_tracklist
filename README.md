# spotify_playlist_from_tracklist
Create a spotify playlist from a track list

Prerequisits:
You need spotify app/api credentials. Noncommercial use is very easy to get. Once you have your client ID and client secret, you can do one of two things: code them in directly into the add_to_playlist.py file or create a local txt file with client id on the first line, client secret on the second line, and username on the third line. You'll also need to specify the path in the config file variable 'CREDS_FILE_PATH.' Or... you can hack into my computer and get them, which would be awesome and terrifying.  

Add the root file of this repo to the Python path. Root folder is currently 'spotify_playlist_from_tracklist'

This is only working for beatport.com top 100 playlists at the moment. The endpoints are configured in config.py. You need to register new endpoints per genre by going to beatport.com, clicking on the genre, and adding in the end of the url e.g.: BREAKS = '/breaks/9'. Once your genre is represented in the file, change the 'GENRE' value to the value of your genre such as 'BREAKS.' No further configurations are needed. 

Run the following:
get_beatport_tracklist.py
add_to_playlist.py

output will appear and overright per genre/month. The output is stricly the failed tracks. You should see a new spotify playlist in your playlists with the tracks that succeeded. I see a 80 to 96% success rate depending on track availability. Further optimizations could be make, but this is a fairly strict search on all artists and remix artists needing to be included. 
