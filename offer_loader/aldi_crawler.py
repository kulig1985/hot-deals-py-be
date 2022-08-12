import urllib.request
from bs4 import BeautifulSoup as bs
import pandas as pd
import re
from datetime import datetime
import numpy as np
import unidecode
from offer_helper import OfferHelper
import requests
import time

class AldiCrawler(OfferHelper):

    def __init__(self, log, config):
        self.log = log
        self.config = config

    def get_fake_headers(self):

        fake_headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:102.0) Gecko/20100101 Firefox/102.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'hu-HU,hu;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cookie': 'sattrack-marketing=true; sattrack-marketing-2=true; sattrack-thirdparty=true; sattrack-thirdparty-2=true; pca-library=1; social-login=1; google-maps-privacy=1; rating-views-privacy=1; accept-youtube-cookie=1; accept-social-share-cookie=yes/1658427677856; AMCV_95446750574EBBDF7F000101%40AdobeOrg=-212117',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'TE': 'trailers',
            'If-None-Match': '6a74a-X'}

        return fake_headers

    def get_all_link_aldi(self):

        all_aldi_link = set()

        #page_aldi_offers = urllib.request.urlopen("https://www.aldi.hu/hu/ajanlatok.html",)



        r = requests.get("https://www.aldi.hu/hu/ajanlatok.html", headers=self.get_fake_headers())
        soup = bs(r.content, features='lxml')
        names = soup.body.findAll('div', {'data-hide-box' : 'false', 'class' : 'item'})

        for name in names:
            for a in name.find_all('a', href=True):
                url = a['href']
                if (url.find('hirlevel') == -1) and (url.find('online-szorolap') == -1):
                    if url.startswith('https'):
                        all_aldi_link.add(url)
                    else:
                        all_aldi_link.add('https://www.aldi.hu' + url)

        return list(all_aldi_link)

    def get_all_offer_aldi(self, all_link):

        all_items = []

        counter = 1

        limit_offer_load = int(self.config.get('MAIN', 'limit_offer_load'))
        if limit_offer_load != 0:
            all_link = all_link[:limit_offer_load]

        for url in all_link:

            try:
                time.sleep(1)
                self.log.debug(f'AldiCrawler crawl url: {url} done {counter} from {len(all_link)}')
                counter = counter + 1

                r = requests.get(url, headers=self.get_fake_headers())
                soup = bs(r.content, features='lxml')
                #page = urllib.request.urlopen(url)
                #soup = bs(page, features='lxml')

                if (url.find('d.') > -1) or (url.find('date.') > -1):
                    self.log.debug(f'{url} is date url')

                    divs = soup.body.findAll('div', {'class': ['col-md-9']})

                    for div in divs:
                        articles = div.findAll('article', {'class': 'wrapper'})

                        for article in articles:

                            item_dict = {}

                            div_prod = article.find('div', {'class': 'item'})

                            item_dict['itemId'] = div_prod['data-productid'].replace('\n', '')

                            item_dict['itemName'] = article.find('h2').get_text().replace('\n', '')
                            item_dict['itemCleanName'] = unidecode.unidecode(item_dict['itemName']).lower()

                            images = article.findAll('img')
                            img_url = np.nan
                            for img in images:
                                img_url = img['data-src']
                                break

                            #item_dict['imageUrl'] = img_url
                            item_dict['imageUrl'] = self.image_download(img_url)

                            item_dict['price'] = article.find('span', {'class': 'price'}).get_text().strip().replace(' Ft',
                                                                                                                     '').replace(
                                ' ', '')

                            measure = article.find('span', {'class': 'additional-product-info'}).get_text().strip()
                            item_dict['measure'] = measure[:measure.find('\n')].replace('/', '')

                            sales_date = article.find('p', {'class': 'availableSoon'})

                            if sales_date != None:

                                date_pattern = r'(?P<group_1>[\d]{4}.[\d]{2}.[\d]{2})'
                                item_dict['salesStart'] = re.search(date_pattern, sales_date.get_text())[0]

                            else:
                                item_dict['salesStart'] = np.nan

                            item_dict['source'] = url[self.find_nth_occurrence(url, '/', 5) + 1:url.find('.html')]
                            item_dict['runDate'] = datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
                            item_dict['shopName'] = 'aldi'
                            item_dict['isSales'] = 1

                            if len(item_dict) > 0:
                                all_items.append(item_dict)

                else:
                    self.log.debug(f'{url} is NOT date url')

                    items = soup.body.findAll('div', {'data-hide-box': 'false', 'class': 'item'})

                    for item in items:

                        item_dict = {}

                        h3 = item.find('h3')
                        h2 = item.find('h2')

                        if (h3 != None) and (h2 != None):

                            try:
                                item_id = item.find('sup').get_text().replace(' ', '')
                                if '/' in item_id:
                                    item_id = item_id[:item_id.find('/')]

                            except Exception as e:

                                item_id = np.nan

                            # print(h3.contents[0])
                            images = item.findAll('img')
                            img_url = np.nan
                            for img in images:
                                img_url = img['data-src']
                                break

                            item_dict['itemId'] = item_id
                            item_dict['itemName'] = h3.contents[0]
                            item_dict['itemCleanName'] = unidecode.unidecode(item_dict['itemName']).lower()
                            #item_dict['imageUrl'] = img_url
                            item_dict['imageUrl'] = self.image_download(img_url)

                            price = h2.find('b')

                            if price != None:
                                price_str_string = price.contents[0]
                                quantity = price_str_string[:price_str_string.find('/')].replace('Ft', '').replace(' ',
                                                                                                                   '').strip()
                                measure = price_str_string[price_str_string.find('/'):].replace('/', '').strip()
                                item_dict['price'] = quantity
                                item_dict['measure'] = measure

                            item_dict['salesStart'] = np.nan

                            item_dict['source'] = url[self.find_nth_occurrence(url, '/', 5) + 1:url.find('.html')]
                            item_dict['runDate'] = datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
                            item_dict['shopName'] = 'aldi'
                            item_dict['isSales'] = 1

                            if len(item_dict) > 0:
                                all_items.append(item_dict)

            except Exception as e:
                self.log.error(f'aldi url exception: {e}')
                continue


        df = pd.DataFrame(all_items)

        df = df.loc[df['price'] != '']

        try:
            df.loc[~df['price'].str.isnumeric(),
                   'price'] = df.loc[~df['price'].str.isnumeric(),
                                     'price'].str[0:df.loc[~df['price'].str.isnumeric(), 'price'].str.find(',').values[0]].astype(int)
        except:
            pass

        df = df.fillna('N.a')
        df = df.loc[df['price'] != '']
        df = df[df['imageUrl'].notnull()]
        df['price'] = df['price'].astype(int)

        return df