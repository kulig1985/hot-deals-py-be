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

    def image_download(self, img_url, shop):

        try:
            if shop == 'spar':

                opener = urllib.request.build_opener()
                opener.addheaders = [('Host', 'cdn1.interspar.at'), (
                'User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:103.0) Gecko/20100101 Firefox/103.0')]

                headers = {'Host': 'cdn1.interspar.at',
                            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:103.0) Gecko/20100101 Firefox/103.0',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                            'Accept-Language': 'hu-HU,hu;q=0.8,en-US;q=0.5,en;q=0.3',
                            'Accept-Encoding': 'gzip, deflate, br',
                            'Connection': 'keep-alive',
                            'Upgrade-Insecure-Requests': '1',
                            'Sec-Fetch-Dest': 'document',
                            'Sec-Fetch-Mode': 'navigate',
                            'Sec-Fetch-Site': 'none',
                            'Sec-Fetch-User': '?1'}

            if shop == 'auchan':

                opener = urllib.request.build_opener()
                opener.addheaders = [('Host', 'ahuazurewebblob0.azureedge.net'), (
                        'User-Agent',
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:103.0) Gecko/20100101 Firefox/103.0')]

                headers = {'Host': 'ahuazurewebblob0.azureedge.net',
                           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:103.0) Gecko/20100101 Firefox/103.0',
                           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                           'Accept-Language': 'hu-HU,hu;q=0.8,en-US;q=0.5,en;q=0.3',
                           'Accept-Encoding': 'gzip, deflate, br',
                           'Connection': 'keep-alive',
                           'Upgrade-Insecure-Requests': '1',
                           'Sec-Fetch-Dest': 'document',
                           'Sec-Fetch-Mode': 'navigate',
                           'Sec-Fetch-Site': 'none',
                           'Sec-Fetch-User': '?1'}

            if shop == 'tesco':

                opener = urllib.request.build_opener()
                opener.addheaders = [('Host', 'secure.ce-tescoassets.com'), (
                        'User-Agent',
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:103.0) Gecko/20100101 Firefox/103.0')]

                headers = {'Host': 'secure.ce-tescoassets.com',
                           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:103.0) Gecko/20100101 Firefox/103.0',
                           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                           'Accept-Language': 'hu-HU,hu;q=0.8,en-US;q=0.5,en;q=0.3',
                           'Accept-Encoding': 'gzip, deflate, br',
                           'Connection': 'keep-alive',
                           'Upgrade-Insecure-Requests': '1',
                           'Sec-Fetch-Dest': 'document',
                           'Sec-Fetch-Mode': 'navigate',
                           'Sec-Fetch-Site': 'none',
                           'Sec-Fetch-User': '?1'}

            if shop == 'lidl':
                opener = urllib.request.build_opener()
                opener.addheaders = [('Host', 'hu.cat-ret.assets.lidl'), (
                        'User-Agent',
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:103.0) Gecko/20100101 Firefox/103.0')]

                headers = {'Host': 'hu.cat-ret.assets.lidl',
                           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:103.0) Gecko/20100101 Firefox/103.0',
                           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                           'Accept-Language': 'hu-HU,hu;q=0.8,en-US;q=0.5,en;q=0.3',
                           'Accept-Encoding': 'gzip, deflate, br',
                           'Connection': 'keep-alive',
                           'Upgrade-Insecure-Requests': '1',
                           'Sec-Fetch-Dest': 'document',
                           'Sec-Fetch-Mode': 'navigate',
                           'Sec-Fetch-Site': 'none',
                           'Sec-Fetch-User': '?1'}

            if shop == 'aldi':
                opener = urllib.request.build_opener()
                opener.addheaders = [('Host', 's7g10.scene7.com'), (
                        'User-Agent',
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:103.0) Gecko/20100101 Firefox/103.0')]

                headers = {'Host': 's7g10.scene7.com',
                            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:103.0) Gecko/20100101 Firefox/103.0',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                            'Accept-Language': 'hu-HU,hu;q=0.8,en-US;q=0.5,en;q=0.3',
                            'Accept-Encoding': 'gzip, deflate, br',
                            'Connection': 'keep-alive',
                            'Sec-Fetch-Dest': 'image',
                            'Sec-Fetch-Mode': 'no-cors',
                            'Sec-Fetch-Site': 'same-origin'}

            uuid_image = uuid.uuid1()
            res = requests.get(img_url, headers=headers)

            if res.headers['Content-Type'][res.headers['Content-Type'].find('/') + 1:] == 'jpeg':
                image_name = shop + '_' + str(uuid_image) + '.jpg'

            if res.headers['Content-Type'][res.headers['Content-Type'].find('/') + 1:] == 'plain':
                image_name = shop + '_' + str(uuid_image) + '.png'

            img_path = '/data/img/' + image_name

            urllib.request.install_opener(opener)

            urllib.request.urlretrieve(img_url, img_path)

            return image_name
        except Exception as e:
            self.log.error(f'image download error: {e}')
            return 'img_error.jpg'
