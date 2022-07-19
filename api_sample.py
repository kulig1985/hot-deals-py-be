from pymongo import MongoClient
from flask import Flask
import logging
from configparser import ConfigParser
import sys
from flask import Response, request
import json
import platform
import unidecode
from bson.json_util import dumps
import re
from bson.objectid import ObjectId

class HotDealsHungaryApi:

    def __init__(self, name):

        self.app = Flask(name)
        self.log = self.load_logger()
        self.config = self.load_config()

        self.user_name = self.config.get('DB', 'user_name')
        self.password = self.config.get('DB', 'password')
        self.mongo_url = f'mongodb://{self.user_name}:{self.password}@95.138.193.102:27017/?authMechanism=DEFAULT'
        self.offer_collection = self.connect_mongo(self.mongo_url, 'offer', 'offerCollection')
        self.offer_listener_collection = self.connect_mongo(self.mongo_url, 'offer', 'offerListener')
        self.shopping_list_collection = self.connect_mongo(self.mongo_url, 'offer', 'shoppingList')
        self.operation_dict = {'boolId': '$set',
                               'checkFlag': '$set',
                               'modDate': '$set',
                               'volume': '$set',
                               'alloweUidList': '$push'}

        @self.app.route('/', methods=['GET'])
        def __index():
            return self.index()

        @self.app.route('/get_offer/<item_name>', methods=['GET'])
        def __get_offer(item_name):
            return self.get_offer(item_name)

        @self.app.route('/get_offer_listener_by_user/<uid>', methods=['GET'])
        def __get_offer_listener_by_user(uid):
            return self.get_offer_listener_by_user(uid)

        @self.app.route('/get_shopping_list_by_user/<uid>', methods=['GET'])
        def __get_shopping_list_by_user(uid):
            return self.get_shopping_list_by_user(uid)

        @self.app.route('/create_offer_listener', methods=['POST'])
        def __create_offer_listener():
            return self.create_offer_listener()

        @self.app.route('/create_shopping_list', methods=['POST'])
        def __create_shopping_list():
            return self.create_shopping_list()

        @self.app.route('/add_item_to_shopping_list', methods=['POST'])
        def __add_item_to_shopping_list():
            return self.add_item_to_shopping_list()

        @self.app.route('/modify_shopping_list_item', methods=['PATCH'])
        def __modify_shopping_list_item():
            return self.modify_shopping_list_item()

        @self.app.route('/modify_shopping_list', methods=['PATCH'])
        def __modify_shopping_list():
            return self.modify_shopping_list()

        @self.app.route('/modify_offer_listener', methods=['PATCH'])
        def __modify_offer_listener():
            return self.modify_offer_listener()

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
                config_path = '/data/hot-deals-py-be/mongo.cfg'
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

            if platform.platform()[:platform.platform().index('-')].lower() == 'macos':
                fh = logging.FileHandler('/Users/kuligabor/Documents/HotDealsHungary/log/hot_deals_api.log',
                                         encoding="utf-8")
            else:
                fh = logging.FileHandler('/data/log/hot_deals_api.log',
                                         encoding="utf-8")
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


    def create_query_param(self, data, fill_value):

        self.log.debug('create_query_param invoked!')

        query_param_dict = {}

        for key in data:
            if not (key == 'id') | \
                   (key == 'offerCollectionId') |\
                   (key == 'removeUser') |\
                   (key == 'itemName') |\
                   (key == 'crDate'):
                #self.log.debug(key)
                if self.operation_dict[key] in query_param_dict.keys():
                    query_param_dict[self.operation_dict[key]].update({fill_value + key: data[key]})
                else:
                    query_param_dict[self.operation_dict[key]] = {fill_value + key: data[key]}

        self.log.debug(query_param_dict)

        return query_param_dict

    def index(self):
        return 'HotDealsHungaryApi'

    def get_offer(self, item_name):

        try:
            item_name = unidecode.unidecode(item_name).lower()
            self.log.debug(f'get_offer invoked with item_name: {item_name}')

            max_key = self.offer_collection.find().sort([("timeKey", -1)]).limit(1).next()['timeKey']
            self.log.debug(f'max_key: {max_key}')

            return Response(dumps(self.offer_collection.find({'$and': [
                                                {'itemCleanName': {'$regex' : r'\b' + item_name + r'\b'}},
                                                {'timeKey': {'$eq': max_key}}
                                                ]})), 200, mimetype='application/json')
        except Exception as e:
            return Response(e, 500, mimetype='application/json')

    def get_offer_listener_by_user(self, uid):
        try:
            self.log.debug(f'get_offer_listener_by_user invoked with uid: {uid}')
            return Response(dumps(self.offer_listener_collection.find({'uid': uid, 'boolId': 1})), 200, mimetype='application/json')

        except Exception as e:
            return Response(e, 500, mimetype='application/json')

    def get_shopping_list_by_user(self, uid):
        try:
            self.log.debug(f'get_shopping_list_by_user invoked with uisd: {uid}')
            return Response(dumps(self.shopping_list_collection.find({'alloweUidList.uid': uid,
                                                                       'alloweUidList.boolId': 1, 'boolId': 1})), 200,
                            mimetype='application/json')

        except Exception as e:
            return Response(e, 500, mimetype='application/json')

    def create_offer_listener(self):
        try:
            data = request.get_json()
            self.log.debug(data)
            mongo_result = self.offer_listener_collection.insert_one(data)
            return Response(dumps({'id': str(mongo_result.inserted_id)}), 201, mimetype='application/json')
        except Exception as e:
            return Response(e, 500, mimetype='application/json')


    def create_shopping_list(self):
        #try:
        data = request.get_json()
        self.log.debug(data)
        mongo_result = self.shopping_list_collection.insert_one(data)
        return Response(dumps({'id' : str(mongo_result.inserted_id)}), 201, mimetype='application/json')
        #except Exception as e:
        #    return Response(e,500, mimetype='application/json')


    def add_item_to_shopping_list(self):
        try:
            data = request.get_json()
            self.log.debug(data)
            mongo_result = self.shopping_list_collection.update_one({"_id": ObjectId(data['id'])},
                                                                    {'$push': {'itemList': data['newItem']}}, upsert=True)

            return Response(dumps({'id': str(mongo_result.matched_count)}), 201, mimetype='application/json')

        except Exception as e:
            return Response(e, 500, mimetype='application/json')

    def modify_shopping_list_item(self):
        try:
            data = request.get_json()
            self.log.debug(data)

            fill_value = 'itemList.$.'
            query_param_dict = self.create_query_param(data, fill_value)

            mongo_result = self.shopping_list_collection.update_one({"_id": ObjectId(data['id']),
                                                                     'itemList.itemDetail.offerCollectionId': data['offerCollectionId']},
                                                                    query_param_dict)

            return Response(dumps({'matchedCount': str(mongo_result.matched_count)}), 201, mimetype='application/json')

        except Exception as e:
            return Response(e, 500, mimetype='application/json')

    def modify_shopping_list(self):
        try:
            data = request.get_json()
            self.log.debug(data)

            fill_value = ''
            query_param_dict = self.create_query_param(data, fill_value)
            find_param = {'_id': ObjectId(data['id'])}

            if data['removeUser'] == 'Y':
                find_param.update({'alloweUidList.uid': data['alloweUidList']['uid']})
                query_param_dict = {'$set': {'alloweUidList.$.boolId': data['alloweUidList']['boolId'],
                                    'alloweUidList.$.modDate': data['alloweUidList']['modDate']}}
                self.log.debug(query_param_dict)
                self.log.debug(find_param)

            mongo_result = self.shopping_list_collection.update_one(
                find_param,
                query_param_dict)

            return Response(dumps({'matchedCount': mongo_result.matched_count}), 201, mimetype='application/json')

        except Exception as e:
            return Response(e, 500, mimetype='application/json')


    def modify_offer_listener(self):

        try:
            data = request.get_json()
            self.log.debug(data)

            fill_value = ''
            query_param_dict = self.create_query_param(data, fill_value)

            mongo_result = self.offer_listener_collection.update_one(
                {'_id': ObjectId(data['id'])}, query_param_dict)

            return Response(dumps({'matchedCount': str(mongo_result.matched_count)}), 201, mimetype='application/json')

        except Exception as e:
            return Response(e, 500, mimetype='application/json')

def main():
    server = HotDealsHungaryApi(__name__)
    server.run(host='0.0.0.0', port=9988)


if __name__ == '__main__':
    main()