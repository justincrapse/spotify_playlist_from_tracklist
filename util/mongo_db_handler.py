
import pymongo


class MDBConnection:
    def __init__(self, db_name='spotify_port', collection_name='track_entries'):
        self.mongo_client = pymongo.MongoClient('localhost', 27017)
        self.db = self.mongo_client[db_name]
        self.collection = self.db[collection_name]  # type: pymongo.collection.Collection

    def set_collection(self, collection_name):
        self.collection = self.db[collection_name]

    def insert_one(self, payload):
        self.collection.insert_one(payload)

    def insert_many(self, document_list):
        self.collection.insert_many(document_list)

    def get_all_spotify_ids(self):
        result = self.collection.find({})
        return [i['spotify_track_id'] for i in result]

    def find_one(self, payload):
        result = self.collection.find_one(payload)
        return result

    def get_cached_playlist(self, genre_url, date):
        result = self.find_one({'genre_url': genre_url, 'datetime': date})
        return result['track_dict_list'] if result else None

    def cache_playlist(self, track_dict_list, genre_url, date):
        payload = {'genre_url': genre_url, 'datetime': date, 'track_dict_list': track_dict_list}
        self.insert_one(payload=payload)


if __name__ == '__main__':
    mdb = MDBConnection()
    mdb.insert_one(payload={'Apples': 44, 'Feeling': 'Awesome'})