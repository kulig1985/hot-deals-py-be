from bs4 import BeautifulSoup as bs
import pandas as pd
from datetime import datetime
import numpy as np
import unidecode
import requests
import time
from offer_helper import OfferHelper


class SparCrawler(OfferHelper):

    def __init__(self, log, config):
        self.log = log
        self.config = config

    def get_fake_headers(self, search):

        if search:
            fake_headers = {'Host': 'search-spar.spar-ics.com',
                            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:102.0) Gecko/20100101 Firefox/102.0',
                            'Accept': 'application/json, text/javascript, */*; q=0.01',
                            'Accept-Language': 'hu-HU,hu;q=0.8,en-US;q=0.5,en;q=0.3',
                            #'Accept-Encoding': 'gzip, deflate, br',
                            'Connection': 'keep-alive',
                            'Origin': 'https://www.spar.hu',
                            'Referer': 'https://www.spar.hu/',
                            'Upgrade-Insecure-Requests': '1',
                            'Sec-Fetch-Dest': 'empty',
                            'Sec-Fetch-Mode': 'corse',
                            'Sec-Fetch-Site': 'cross-site'}
        else:
            fake_headers = {'Host': 'www.spar.hu',
                            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:102.0) Gecko/20100101 Firefox/102.0',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                            'Accept-Language': 'hu-HU,hu;q=0.8,en-US;q=0.5,en;q=0.3',
                            #'Accept-Encoding': 'gzip, deflate, br',
                            'Connection': 'keep-alive',
                            'Upgrade-Insecure-Requests': '1',
                            'Sec-Fetch-Dest': 'document',
                            'Sec-Fetch-Mode': 'navigate',
                            'Sec-Fetch-Site': 'none',
                            'Sec-Fetch-User': '?1',
                            'TE': 'trailers'}


        return fake_headers

    def get_all_link_spar(self):

        offer_page = 'https://www.spar.hu/onlineshop/'

        r = requests.get(offer_page, headers=self.get_fake_headers(search=False))
        soup = bs(r.content, features='lxml')
        a_list = soup.body.findAll('a', {'class': ['flyout-categories__link']})
        all_spar_link = set()
        for a in a_list:
            if a['href'] != 'javascript:void(0)':
                ref = a['href']
                base_string = 'https://search-spar.spar-ics.com/fact-finder/rest/v4/search/products_lmos_hu?query=*&q=*&hitsPerPage=1000&filter=category-path:'
                categ = ref[ref.find('/c/'):].replace('/c/', '').replace('/', '')
                all_spar_link.add(base_string + categ)

        return list(all_spar_link)

    def get_all_offer_spar(self, all_spar_link):

        all_items = []
        counter = 1

        limit_offer_load = int(self.config.get('MAIN', 'limit_offer_load'))
        if limit_offer_load != 0:
            all_spar_link = all_spar_link[:limit_offer_load]

        for url in all_spar_link: #TODO remove it!

            try:
                time.sleep(1)
                response = requests.get(url, headers=self.get_fake_headers(search=True))
                self.log.debug(f'SparCrawler crawl url: {url} done {counter} from {len(all_spar_link)}')
                counter = counter + 1
                for hit in response.json()['hits']:

                    item_dict = {}
                    item_dict['itemId'] = hit['masterValues']['product-number']
                    item_dict['itemName'] = hit['masterValues']['title']
                    item_dict['itemCleanName'] = unidecode.unidecode(item_dict['itemName']).lower()
                    #item_dict['imageUrl'] = hit['masterValues']['image-url']
                    item_dict['imageUrl'] = self.image_download(hit['masterValues']['image-url'], spar=True)
                    item_dict['price'] = hit['masterValues']['price']
                    item_dict['measure'] = hit['masterValues']['sales-unit']
                    item_dict['salesStart'] = np.nan
                    item_dict['source'] = 'spar'
                    item_dict['runDate'] = datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
                    item_dict['shopName'] = 'spar'
                    if (hit['masterValues']['regular-price'] != hit['masterValues']['price']):
                        item_dict['isSales'] = 1
                    else:
                        item_dict['isSales'] = 0

                    all_items.append(item_dict)

            except Exception as e:
                self.log.error(f'spar url error: {e}')
                continue

        df = pd.DataFrame(all_items)
        df = df.fillna('N.a')
        df = df.loc[df['price'] != '']
        df = df[df['imageUrl'].notnull()]
        df['price'] = df['price'].astype(int)

        return df