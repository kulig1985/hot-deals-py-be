import logging
import platform
import sys
from abc import ABC
from configparser import ConfigParser
import os
import time

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

    def remove_old_images(self):

        dir = '/data/img/'
        now = time.time()

        for f in os.listdir(dir):
            if os.stat(os.path.join(dir, f)).st_mtime < now - 3 * 86400:
                os.remove(os.path.join(dir, f))

        self.log.debug('all 7 days old files removed from /data/img/')

