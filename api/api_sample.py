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
from flask import send_file
import model.shopping_list_complex_model as slc
#import model.offer_response as ofre

class HotDealsHungaryApi:

    def __init__(self, name):

        self.app = Flask(name)
        self.log = self.load_logger()
        self.config = self.load_config()

        self.user_name = self.config.get('DB', 'user_name')
        self.password = self.config.get('DB', 'password')
        self.host = self.config.get('DB', 'host')
        self.mongo_url = f'mongodb://{self.user_name}:{self.password}{self.host}'
        self.offer_collection = self.connect_mongo(self.mongo_url, 'offer', 'offerCollection')
        self.offer_listener_collection = self.connect_mongo(self.mongo_url, 'offer', 'offerListener')
        self.shopping_list_collection = self.connect_mongo(self.mongo_url, 'offer', 'shoppingList')
        self.operation_dict = {'boolId': '$set',
                               'checkFlag': '$set',
                               'modDate': '$set',
                               'volume': '$set',
                               'itemCount': '$inc',
                               'listName': '$set',
                               'alloweUidList': '$push'}

        @self.app.route('/', methods=['GET'])
        def __index():
            return self.index()

        @self.app.route('/get_offer/<item_name>', methods=['GET'])
        def __get_offer(item_name):
            return self.get_offer(item_name)

        @self.app.route('/add_offer', methods=['POST'])
        def __add_offer():
            return self.add_offer()

        @self.app.route('/find_offer_by_id/<id>', methods=['GET'])
        def __find_offer_by_id(id):
            return self.find_offer_by_id(id)


        @self.app.route('/get_offer_listener_by_user/<uid>', methods=['GET'])
        def __get_offer_listener_by_user(uid):
            return self.get_offer_listener_by_user(uid)

        @self.app.route('/get_shopping_list_by_user/<uid>/<shoppinglist_id>', methods=['GET'])
        def __get_shopping_list_by_user(uid,shoppinglist_id):
            return self.get_shopping_list_by_user(uid,shoppinglist_id)

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

        @self.app.route('/image_download/<image_name>', methods=['GET'])
        def __image_download(image_name):
            return self.image_download(image_name)

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
                config_path = './py_be_config_loader.cfg'
            else:
                config_path = '/data/hot-deals-py-be/py_be_config_loader.cfg'
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
                   (key == 'offerCollectionId') | \
                   (key == 'offerListenerEntityId') | \
                   (key == 'removeUser') |\
                   (key == 'itemName') |\
                   (key == 'crDate'):
                self.log.debug(key)
                if self.operation_dict[key] in query_param_dict.keys():
                    query_param_dict[self.operation_dict[key]].update({fill_value + key: data[key]})
                else:
                    query_param_dict[self.operation_dict[key]] = {fill_value + key: data[key]}

        self.log.debug(query_param_dict)

        return query_param_dict

    def index(self):
        return 'HotDealsHungaryApi'

    def image_download(self, image_name):
        path = '/data/img/'
        return send_file(path + image_name, mimetype='image/jpeg')

    def get_offer(self, item_name):

        #try:
        item_name = unidecode.unidecode(item_name).lower()
        self.log.debug(f'get_offer invoked with item_name: {item_name}')

        max_key = self.offer_collection.find().sort([("timeKey", -1)]).limit(1).next()['timeKey']
        self.log.debug(f'max_key: {max_key}')

        '''
        return dumps(self.offer_collection.find({'$and': [
                                            {'itemCleanName': {'$regex' : r'\b' + item_name + r'\b'}},
                                            {'timeKey': {'$eq': max_key}},
                                            {'isSales': 1},
                                            {'insertType': 'automate'}
                                            ]}))

        '''

        pipeline = [{'$match':  {'$and': [
                                            {'itemCleanName': {'$regex': r'\b' + item_name + r'\b'}},
                                            {'timeKey': {'$eq': max_key}},
                                            {'isSales': 1},
                                            {'insertType': 'automate'}
                                            ]}}, {'$addFields': {"id": '$_id'}}, {'$project': {'_id': 0}}]
        '''
        return Response(dumps(self.offer_collection.find({'$and': [
                                            {'itemCleanName': {'$regex' : r'\b' + item_name + r'\b'}},
                                            {'timeKey': {'$eq': max_key}},
                                            {'isSales': 1},
                                            {'insertType': 'automate'}
                                            ]})), 200, mimetype='application/json')
    
        '''

        def remove_oid(string):
            while True:
                pattern = re.compile('{\s*"\$oid":\s*(\"[a-z0-9]{1,}\")\s*}')
                match = re.search(pattern, string)
                if match:
                    string = string.replace(match.group(0), match.group(1))
                else:
                    return string

        return Response(remove_oid(dumps(self.offer_collection.aggregate(pipeline))), 200,
                        mimetype='application/json')

        # except Exception as e:
        #    return Response(e, 500, mimetype='application/json')
            # return None

    def add_offer(self):
        try:
            data = request.get_json()
            self.log.debug(data)
            mongo_result = self.offer_collection.insert_one(data)
            return Response(dumps({'id': str(mongo_result.inserted_id)}), 201, mimetype='application/json')
        except Exception as e:
            return Response(e, 500, mimetype='application/json')

    def find_offer_by_id(self, id):

        try:
            return Response(dumps(self.offer_collection.find_one({"_id": ObjectId(id)})), 200,
                            mimetype='application/json')

        except Exception as e:
            return Response(e, 500, mimetype='application/json')


    def get_offer_listener_by_user(self, uid):
        try:
            self.log.debug(f'get_offer_listener_by_user invoked with uid: {uid}')
            return Response(dumps(self.offer_listener_collection.find({'uid': uid, 'boolId': 1})), 200, mimetype='application/json')

        except Exception as e:
            return Response(e, 500, mimetype='application/json')

    def get_shopping_list_by_user(self, uid, shoppinglist_id):
        try:
            self.log.debug(f'get_shopping_list_by_user invoked with uisd: {uid} - shoppinglist_id: {shoppinglist_id}')

            '''
            pipeline = [{"$match": {
                         "alloweUidList": {
                         "$elemMatch": {
                              "uid": uid,
                              "boolId": 1
                            }},
                              "boolId": 1
                            }},
                        {"$addFields": {
                              "itemList": {
                                "$filter": {
                                  "input": "$itemList",
                                  "as": "i",
                                  "cond": {
                                    "$eq": [
                                      "$$i.boolId",
                                      1
                                    ]}}}}}]
            

            pipeline = [{"$match": {
                "alloweUidList": {
                    "$elemMatch": {
                        "uid": uid,
                        "boolId": 1
                    }},
                "boolId": 1
            }}]
            '''

            pipeline = [{"$match": {
                            "alloweUidList": {
                            "$elemMatch": {
                            "uid": uid,
                            "boolId": 1
                            }},
                            "boolId": 1,
                            }},
                            {"$addFields": {
                                  "offerModelList": {
                                    "$filter": {
                                      "input": "$offerModelList",
                                      "as": "i",
                                      "cond": {
                                        "$eq": [
                                          "$$i.offerListenerEntity.boolId",
                                          1
                                        ]}}}},
                            },
                            {
                            "$set": {
                                    "offerModelList": {
                                    "$map": {
                                    "input": "$offerModelList",
                                    "as": "offerModel",
                                    "in": {
                                    "$mergeObjects": [
                                        "$$offerModel",
                                            {
                                                "offers": {
                                                "$filter": {
                                                "input": "$$offerModel.offers",
                                                "as": "x",
                                                "cond": {
                                                "$eq": [
                                                "$$x.isSelectedFlag",
                                                1]
                            }}}}]}}}}}]
            # "_id": ObjectId(shoppinglist_id)

            if (shoppinglist_id != 'none'):
                pipeline[0]["$match"]["_id"] = ObjectId(shoppinglist_id)

            self.log.debug(pipeline)

            return Response(dumps(self.shopping_list_collection.aggregate(pipeline)), 200,
                                                                          mimetype='application/json')

        except Exception as e:
            return Response(e, 500, mimetype='application/json')

    def create_offer_listener(self):
        #try:
        data = request.get_json()
        self.log.debug(data)
        # mongo_result = self.offer_listener_collection.insert_one(data)
        # return Response(dumps({'id': str(mongo_result.inserted_id)}), 201, mimetype='application/json')

        # choosen_shopping_list = json.loads(dumps(self.shopping_list_collection.find_one({"_id": ObjectId(data['shoppingListId'])})))

        # self.log.debug(f'choosen_shopping_list: {choosen_shopping_list["_id"]}')

        # choosen_shopping_list_instance = slc.shopping_list_complex_model_from_dict(choosen_shopping_list)

        dummy_id = slc.ID(oid='0')
        new_offer_listener = slc.OfferListenerEntity(dummy_id,
                                                     data['uid'],
                                                     data['itemName'],
                                                     data['crDate'],
                                                     data['boolId'],
                                                     None,
                                                     data['imageColorIndex'],
                                                     data['shoppingListId'],
                                                     data['checkFlag'],
                                                     data['itemCount'])

        new_offer_listener_instance = new_offer_listener.to_dict()
        del new_offer_listener_instance['_id']
        self.log.debug(f'new_offer_listener_instance before insert: {new_offer_listener_instance}')

        mongo_result = self.offer_listener_collection.insert_one(new_offer_listener_instance)

        self.log.debug(f'offer_listener_mongo_result: {str(mongo_result.inserted_id)}')

        offer_listener_id = mongo_result.inserted_id

        inserted_id = slc.ID(oid=str(mongo_result.inserted_id))
        new_offer_listener_instance['_id'] = inserted_id.to_dict()
        self.log.debug(f'new_offer_listener_instance after insert: {new_offer_listener_instance}')

        # offer_list = self.get_offer(new_offer_listener_instance['itemName'])

        # offer_object_list = slc.offers_to_dict(slc.offers_from_dict(json.loads(offer_list)))

        def extract_price(value_dict):
            try:
                return int(value_dict['price'])
            except KeyError:
                return 99999

        # offer_object_list.sort(key=extract_price, reverse=False)

        # self.log.debug(f'offer_object_list {offer_object_list}')

        # offer_model_instance = slc.OfferModelList(slc.OfferListenerEntity.from_dict(new_offer_listener_instance),
        #                                           slc.offers_from_dict(offer_object_list))

        offer_model_instance = slc.OfferModelList(slc.OfferListenerEntity.from_dict(new_offer_listener_instance), [])

        self.log.debug(f'offer_model_instance: {offer_model_instance}')

        self.log.debug(f'offer_model_instance: {slc.offer_model_list_to_dict(offer_model_instance)}')

        offer_model_instance_to_insert = slc.offer_model_list_to_dict(offer_model_instance)

        offer_model_instance_to_insert['offerListenerEntity']['_id'] = offer_model_instance_to_insert['offerListenerEntity']['_id']['$oid']

        # for offer in offer_model_instance_to_insert['offers']:
        #    offer['_id'] = offer['_id']['$oid']

        self.log.debug(f'offer_model_instance: {offer_model_instance_to_insert}')


        mongo_result = self.shopping_list_collection.update_one({"_id": ObjectId(data['shoppingListId'])},
                                                                {'$push': {'offerModelList': offer_model_instance_to_insert}},
                                                                upsert=True)

        return Response(dumps({'id': str(offer_listener_id)}), 201, mimetype='application/json')

        # return Response(dumps({'id': str(mongo_result.inserted_id)}), 201, mimetype='application/json')
        # except Exception as e:
        #    return Response(e, 500, mimetype='application/json')



    def create_shopping_list(self):
        #try:
        data = request.get_json()
        self.log.debug(data)
        mongo_result = self.shopping_list_collection.insert_one(data)
        return Response(dumps({'id' : str(mongo_result.inserted_id)}), 201, mimetype='application/json')
        #except Exception as e:
        #    return Response(e,500, mimetype='application/json')


    def add_item_to_shopping_list(self):
        #try:
        data = request.get_json()
        self.log.debug(data)

        self.shopping_list_collection.update_one({"_id": ObjectId(data['id']),
                                                  "offerModelList.offerListenerEntity._id": data['offerListenerId']},
                                                 {'$set': {'offerModelList.$.offers.$[].isSelectedFlag': 0}})

        mongo_result = self.shopping_list_collection.update_one({"_id": ObjectId(data['id']),
                                                                 "offerModelList.offerListenerEntity._id": data['offerListenerId']},
                                                                {'$push': {'offerModelList.$.offers': data['offer']}}, upsert=True)

        return Response(dumps({'id': str(mongo_result.matched_count)}), 201, mimetype='application/json')

        #except Exception as e:
        #    return Response(e, 500, mimetype='application/json')

    def modify_shopping_list_item(self):

        '''
        {"id":"630fb2daaaf01cf588f51427",
        "offerListenerEntityId":"630fb305aaf01cf588f51428",
        "itemCount": 1}

        {"id":"630fb2daaaf01cf588f51427",
        "offerListenerEntityId":"630fb305aaf01cf588f51428",
        "checkFlag": 1}

        {"id":"630fb2daaaf01cf588f51427",
        "offerListenerEntityId":"630fb305aaf01cf588f51428",
        "boolId": 1}

        :return:
        '''

        #try:
        data = request.get_json()
        self.log.debug(data)

        #fill_value = 'itemList.$.'
        fill_value = 'offerModelList.$.offerListenerEntity.'
        query_param_dict = self.create_query_param(data, fill_value)

        self.log.debug(f'query_param_dict: {query_param_dict}')

        mongo_result = self.shopping_list_collection.update_one({"_id": ObjectId(data['id']),
                                                                 'offerModelList.offerListenerEntity._id': data['offerListenerEntityId']},
                                                                query_param_dict)

        return Response(dumps({'matchedCount': str(mongo_result.matched_count)}), 201, mimetype='application/json')

        # except Exception as e:
        #    return Response(e, 500, mimetype='application/json')

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