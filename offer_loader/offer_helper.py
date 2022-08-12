import uuid
import urllib.request
import requests
import os


class OfferHelper():

    def find_nth_occurrence(self, string, char, occurrence):

        val = -1
        for i in range(0, occurrence):
            val = string.find(char, val + 1)
        return val

    def image_download(self, img_url, spar=False):

        try:
            uuid_image = uuid.uuid1()
            res = requests.get(img_url)

            if res.headers['Content-Type'][res.headers['Content-Type'].find('/') + 1:] == 'jpeg':
                image_name = str(uuid_image) + '.jpg'

            if res.headers['Content-Type'][res.headers['Content-Type'].find('/') + 1:] == 'plain':
                image_name = str(uuid_image) + '.png'

            img_path = '/data/img/' + image_name

            if spar:

                opener = urllib.request.build_opener()
                opener.addheaders = [('Host', 'cdn1.interspar.at'), (
                'User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:103.0) Gecko/20100101 Firefox/103.0')]

                urllib.request.install_opener(opener)

            urllib.request.urlretrieve(img_url, img_path)

            return image_name
        except Exception as e:
            self.log.error(f'image download error: {e}')
            return 'img_error.jpg'
