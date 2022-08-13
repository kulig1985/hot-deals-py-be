import urllib.request
from bs4 import BeautifulSoup as bs
import re
import pandas as pd
from datetime import datetime
import numpy as np
import unidecode
from offer_helper import OfferHelper
import requests
import time

class LidlCrawler(OfferHelper):

    def __init__(self, log, config):
        self.log = log
        self.config = config

    def get_fake_headers(self):

        fake_headers = {
            'Host': 'www.lidl.hu',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:102.0) Gecko/20100101 Firefox/102.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'hu-HU,hu;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cookie': 'CookieConsent={stamp:%27bNhItFfBZeXSlwNo3fU46j1EmvwJ9CKv+X4cWKUX8HiBBOMIhdo/RA==%27%2Cnecessary:true%2Cpreferences:true%2Cstatistics:true%2Cmarketing:true%2Cver:1%2Cutc:1655903840313%2Cregion:%27hu%27}; _gcl_au=1.1.1540839504.1655903841; dtou=5AE18F867922B5AD76623D621651A8B8; _ga=GA1.2.1818578403.1655903841; dt_sc=nbxwnhxfef2wdowotdyziy5u%7C1657779958641',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'}

        return fake_headers

    def get_all_link_lidl(self):

        #offer_page = 'https://www.lidl.hu/ajanlataink'

        #page = urllib.request.urlopen(offer_page)
        #soup = bs(page, features='lxml')
        r = requests.get("https://www.lidl.hu/ajanlataink", headers=self.get_fake_headers())
        soup = bs(r.content, features='lxml')

        divs_body = soup.body.findAll('div', {'class': ['tabnavaccordion__content']})

        all_link = []
        for div in divs_body:
            for a in div.find_all('a', href=True):
                url = 'https://www.lidl.hu' + a['href']
                all_link.append(url)

        return all_link

    def get_all_offer_lidl(self, all_link):

        all_items = []

        counter = 1

        limit_offer_load = int(self.config.get('MAIN', 'limit_offer_load'))
        if limit_offer_load != 0:
            all_link = all_link[:limit_offer_load]

        for url in all_link:

            try:
                time.sleep(1)
                self.log.debug(f'crawl url: {url} done {counter} from {len(all_link)}')
                counter = counter + 1

                #page = urllib.request.urlopen(url)
                #soup = bs(page, features='lxml')
                r = requests.get(url, headers=self.get_fake_headers())
                soup = bs(r.content, features='lxml')

                divs = soup.body.findAll('div', {'class': ['nuc-a-flex-item']})

                for div in divs:
                    articles = div.findAll('article', {'class': 'ret-o-card'})
                    for article in articles:

                        item_dict = {}

                        item_dict['itemId'] = article['data-id']

                        brand = article.find('p', {'class': 'ret-o-card__content'})

                        if brand != None:

                            item_dict['itemName'] = article['data-name'] + ' - ' + brand.get_text().strip()
                        else:
                            item_dict['itemName'] = article['data-name']

                        item_dict['itemCleanName'] = unidecode.unidecode(item_dict['itemName']).lower()

                        images = article.findAll('img')
                        img_url = np.nan
                        for img in images:
                            img_url = img['src']
                            break

                        #item_dict['imageUrl'] = img_url
                        item_dict['imageUrl'] = self.image_download(img_url=img_url, shop='lidl')

                        item_dict['price'] = article['data-price']

                        measure = article.find('div', {'class': 'lidl-m-pricebox__basic-quantity'})

                        if measure != None:
                            item_dict['measure'] = measure.get_text()
                        else:
                            item_dict['measure'] = np.nan

                        sales_from_pattern = r'(?P<group_1>[\d]{2}.[\d]{2})'

                        if (article['data-list'] != None) and (re.search(sales_from_pattern, article['data-list']) != None):

                            sales_data = article['data-list']
                            item_dict['salesStart'] = str(datetime.now().year) + '.' + re.search(sales_from_pattern,
                                                                                                 article['data-list'])[0]
                        else:
                            item_dict['salesStart'] = np.nan

                        cut_url = url[self.find_nth_occurrence(url, '/', 4) + 1:]

                        item_dict['source'] = cut_url[:cut_url.find('/')]
                        item_dict['runDate'] = datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
                        item_dict['shopName'] = 'lidl'
                        item_dict['isSales'] = 1

                        if len(item_dict) > 0:
                            all_items.append(item_dict)

            except Exception as e:
                self.log.error(f'lidl url exception: {e}')
                continue

        df = pd.DataFrame(all_items)
        df = df.fillna('N.a')
        df = df.loc[df['price'] != '']
        df = df[df['imageUrl'].notnull()]
        df['price'] = df['price'].astype(int)

        return df