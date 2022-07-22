import pandas as pd
from datetime import datetime
import numpy as np
import unidecode
import requests
from offer_helper import OfferHelper
import time

class AuchanCrawler(OfferHelper):

    def __init__(self, log):
        self.log = log

    def get_auth_header(self, token):

        auth_header = {'Authorization': 'Bearer ' + token,
                       'Host': 'online.auchan.hu',
                       'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:102.0) Gecko/20100101 Firefox/102.0',
                       'Accept': 'application/json',
                       'Accept-Language': 'hu',
                       'Accept-Encoding': 'gzip, deflate, br',
                       'Connection': 'keep-alive',
                       'Referer': 'https://online.auchan.hu/',
                       'Sec-Fetch-Dest': 'empty',
                       'Sec-Fetch-Mode': 'cors',
                       'Sec-Fetch-Site': 'same-origin',
                       'TE': 'trailers'}

        return auth_header

    def get_auchan_token(self):

        token_url = 'https://online.auchan.hu/'

        fake_headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:102.0) Gecko/20100101 Firefox/102.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'hu-HU,hu;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cookie': 'stg_externalReferrer=; stg_last_interaction=Tue%2C%2019%20Jul%202022%2015:56:21%20GMT; stg_returning_visitor=Tue%2C%2019%20Jul%202022%2015:56:21%20GMT; stg_traffic_source_priority=5',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'TE': 'trailers',
            'If-None-Match': '6a74a-X'}

        response = requests.get(token_url, headers=fake_headers)

        token = response.headers['Set-Cookie'][response.headers['Set-Cookie'].find('access_token='):]
        token = token[:token.find(';')].replace('access_token=', '')

        return token

    def get_all_auchan_link(self, token):
        auchan_tree_url = 'https://online.auchan.hu/api/v2/tree/0?hl=hu&'

        response = requests.get(auchan_tree_url, headers=self.get_auth_header(token))
        item_url = 'https://online.auchan.hu/api/v2/products?categoryId={id}&itemsPerPage={itemCount}&page=1&hl=hu'

        all_auchan_link = []
        for child in response.json()['children']:
            for sub_child in child['children']:
                for sub_sub_child in sub_child['children']:
                    page_url = item_url.format(id=sub_sub_child['id'], itemCount=sub_sub_child['productCount'])
                    all_auchan_link.append(page_url)

        return all_auchan_link


    def get_all_offer_auchan(self, all_auchan_link, token):

        all_items = []
        counter = 1
        for link in all_auchan_link:

            try:
                time.sleep(1)
                self.log.debug(f'AuchanCrawler crawl url: {link} done {counter} from {len(all_auchan_link)}')
                response = requests.get(link, headers=self.get_auth_header(token))
                counter = counter + 1

                for result in response.json()['results']:
                    try:
                        item_dict = {}
                        item_dict['itemId'] = result['id']
                        item_dict['itemName'] = result['defaultVariant']['name']
                        item_dict['itemCleanName'] = unidecode.unidecode(item_dict['itemName']).lower()
                        item_dict['imageUrl'] = result['defaultVariant']['media']['mainImage']
                        item_dict['price'] = result['defaultVariant']['price']['gross']
                        item_dict['measure'] = result['defaultVariant']['packageInfo']['packageUnit']
                        item_dict['salesStart'] = np.nan
                        item_dict['source'] = result['categoryName']
                        item_dict['runDate'] = datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
                        item_dict['shopName'] = 'auchan'
                        if (result['defaultVariant']['price']['isDiscounted']):
                            item_dict['isSales'] = 1
                        else:
                            item_dict['isSales'] = 0

                        all_items.append(item_dict)

                    except Exception as e:
                        self.log.error(f'auchan item error: {e}')
                        continue

            except Exception as e:
                self.log.debug(f'auchan url error: {e}')
                continue

        df = pd.DataFrame(all_items)
        df = df.fillna('N.a')
        df = df.loc[df['price'] != '']
        df = df[df['imageUrl'].notnull()]
        df['price'] = df['price'].astype(int)

        return df