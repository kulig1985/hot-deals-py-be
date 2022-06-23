from pymongo import MongoClient
from flask import Flask
import logging
from configparser import ConfigParser
import sys
from flask import Response
import json
import platform
import unidecode
from bson.json_util import dumps

class HotDealsHungaryApi:

    def __init__(self, name):

        self.app = Flask(name)
        self.log = self.load_logger()
        self.config = self.load_config()

        self.user_name = self.config.get('DB', 'user_name')
        self.password = self.config.get('DB', 'password')
        self.mongo_url = f'mongodb://{self.user_name}:{self.password}@95.138.193.102:27017/?authMechanism=DEFAULT'
        self.collection = self.connect_mongo(self.mongo_url, 'offer', 'offer-collection')

        @self.app.route('/')
        def __index():
            return self.index()

        @self.app.route('/get_offer/<item_name>', methods=['GET'])
        def __get_offer(item_name):
            return self.get_offer(item_name)

    def run(self, host, port):
        self.app.run(host=host, port=port)

    def connect_mongo(self, mongo_url, db, collection):

        client = MongoClient(mongo_url)
        db = client[db]
        collection = db[collection]

        return collection


    def load_config(self):
        try:
            self.log.info("Config file load begin")
            config = ConfigParser()

            if platform.platform()[:platform.platform().index('-')].lower() == 'macos':
                config_path = '/Users/kuligabor/Documents/HotDealsHungary/hot-deals-py-be/mongo.cfg'
            else:
                config_path = '/data/flight/flight_search_py_be/kiwi.cfg'
            config.read(config_path, encoding='utf-8')

            self.log.info("Config file load end")
            return config
        except Exception as e:
            self.log.error("Config file load error: {}".format(str(e)))
            sys.exit(1)

    def load_logger(self):

        try:
            log = logging.getLogger('LOG')
            log.setLevel(logging.DEBUG)
            fh = logging.FileHandler('hot_deals_api.log', encoding="utf-8")
            fh.setLevel(logging.DEBUG)

            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)

            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            ch.setFormatter(formatter)
            fh.setFormatter(formatter)

            log.addHandler(ch)
            log.addHandler(fh)
            log.info('Logger set')

            return log

        except Exception as e:
            print("logger error: " + str(e))
            sys.exit(1)

    def index(self):
        return 'HotDealsHungaryApi'

    def get_offer(self, item_name):
        return Response(dumps(self.collection.find({'itemCleanName': {'$regex': unidecode.unidecode(item_name)}})), mimetype='application/json')

def main():
    server = HotDealsHungaryApi(__name__)
    server.run(host='0.0.0.0', port=9988)

if __name__ == '__main__':
    main()