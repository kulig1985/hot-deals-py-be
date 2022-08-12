import logging
import platform
import sys
from abc import ABC
from configparser import ConfigParser
import uuid
import urllib.request
import requests
import os

class Base(ABC):

    def __init__(self):
        self.log = self.load_logger()
        self.config = self.load_config()

    def load_logger(self):

        try:
            log = logging.getLogger('LOG')
            log.setLevel(logging.DEBUG)

            if platform.platform()[:platform.platform().index('-')].lower() == 'macos':
                fh = logging.FileHandler('/Users/kuligabor/Documents/HotDealsHungary/log/offer_loader.log',
                                         encoding="utf-8")
            else:
                fh = logging.FileHandler('/data/log/offer_loader.log',
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

    def load_config(self):
        try:
            self.log.info("Config file load begin")
            config = ConfigParser()

            if platform.platform()[:platform.platform().index('-')].lower() == 'macos':
                config_path = '/Users/kuligabor/Documents/HotDealsHungary/hot-deals-py-be/py_be_config_loader.cfg'
            else:
                config_path = '/data/hot-deals-py-be/py_be_config_loader.cfg'

            config.read(config_path, encoding='utf-8')

            self.log.info("Config file load end")
            return config
        except Exception as e:
            self.log.error("Config file load error: {}".format(str(e)))
            sys.exit(1)

    def image_download(self, img_url):

        try:
            uuid_image = uuid.uuid1()
            res = requests.get(img_url)

            if res.headers['Content-Type'][res.headers['Content-Type'].find('/') + 1:] == 'jpeg':
                image_name = str(uuid_image) + '.jpg'

            if res.headers['Content-Type'][res.headers['Content-Type'].find('/') + 1:] == 'plain':
                image_name = str(uuid_image) + '.png'

            img_path = '/data/img/' + image_name
            urllib.request.urlretrieve(img_url, img_path)

            return image_name
        except Exception as e:
            self.log.error(f'image download error: {e}')
            return 'img_error.jpg'

    def remove_old_images(self):

        dir = '/data/img/'
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))

        self.log.debug('all files removed from /data/img/')
