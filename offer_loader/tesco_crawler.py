from bs4 import BeautifulSoup as bs
import re
import pandas as pd
from datetime import datetime
import numpy as np
import unidecode
import requests
from offer_helper import OfferHelper
import time

class TescoCrawler(OfferHelper):

    def __init__(self, log):
        self.log = log

    def get_fake_headers(self):

        fake_headers = {'Host': 'bevasarlas.tesco.hu',
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:102.0) Gecko/20100101 Firefox/102.0',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                        'Accept-Language': 'hu-HU,hu;q=0.8,en-US;q=0.5,en;q=0.3',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive',
                        'Referer': 'https://www.spar.hu/',
                        'Sec-Fetch-Dest': 'empty',
                        'Sec-Fetch-Mode': 'cors',
                        'Sec-Fetch-Site': 'none',
                        'Upgrade-Insecure-Requests': '1',
                        'Sec-Fetch-User': '?1',
                        'TE': 'trailers'}

        return fake_headers

    def get_all_tesco_link(self):


        offer_page = 'https://bevasarlas.tesco.hu/groceries/hu-HU/'

        r = requests.get(offer_page, headers=self.get_fake_headers())
        soup = bs(r.content, features='lxml')

        divs_body = soup.body.findAll('div',
                                      {'class': ['menu-tree main-level-menu-tree--open menu-tree--hide-down-chevrons']})

        all_link = []
        for div in divs_body:
            for a in div.find_all('a', href=True):
                find_value = a['href']
                find_value = find_value[:find_value.find('?')]
                url = 'https://bevasarlas.tesco.hu' + find_value + '/all?include-children=true'
                # print(url)
                all_link.append(url)

        all_tesco_link = set()

        for link in all_link:
            #print(link)
            r = requests.get(link, headers=self.get_fake_headers())
            soup = bs(r.content, features='lxml')

            divs_pagi = soup.body.findAll('div', {'class': ['pagination__items-displayed']})

            for div in divs_pagi:
                for strong in div.findAll('strong'):
                    if strong.text.find('termékből') > -1:
                        number = int(re.findall(r'\d+', strong.text)[0])
                        const = 20
                        div = number // const
                        div_rem = number % const
                        query = '&page={num}&count={const}'
                        for x in range(1, div + 2):
                            url_extend = link + query.format(num=x, const=const)
                            #print(url_extend)
                            all_tesco_link.add(url_extend)

        return list(all_tesco_link)

    def get_all_offer_tesco(self, all_tesco_link):

        all_items = []
        counter = 1

        for t_link in all_tesco_link[:2]: #TODO remove it!

            try:
                time.sleep(3)
                self.log.debug(f'TescoCrawler crawl url: {t_link} done {counter} from {len(all_tesco_link)}')
                counter = counter + 1

                r = requests.get(t_link, headers=self.get_fake_headers())
                soup = bs(r.content, features='lxml')

                divs_list_page = soup.body.findAll('div', {'class': ['product-lists-wrapper']})

                for div in divs_list_page:

                    cards = div.findAll('li', {'class': 'product-list--list-item'})
                    for card in cards:
                        try:
                            item_dict = {}

                            id_link = card.find('a', {'class': 'product-image-wrapper'})['href']
                            item_dict['itemId'] = id_link[self.find_nth_occurrence(id_link, '/', 4) + 1:]
                            name = card.find('span', {'class': 'beans-link__text'})
                            item_dict['itemName'] = name.text

                            item_dict['itemCleanName'] = unidecode.unidecode(item_dict['itemName']).lower()

                            img = card.find('img', {'class': 'product-image'})
                            img_url = img['srcset']
                            item_dict['imageUrl'] = img_url[:img_url.find(' ')]

                            price = card.find('p', {'class': 'beans-price__text'})
                            item_dict['price'] = price.text.replace(' Ft', '').replace(' ','').strip()

                            measure = card.find('p', {'class': 'beans-price__subtext'})
                            item_dict['measure'] = measure.text

                            item_dict['salesStart'] = np.nan

                            item_dict['source'] = t_link[t_link.find('/shop'):self.find_nth_occurrence(t_link, '/', 7)].replace(
                                '/shop/', '')

                            item_dict['runDate'] = datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
                            item_dict['shopName'] = 'tesco'

                            special = card.find('div', {'class': 'special-offer-sash'})

                            if special != None:
                                item_dict['isSales'] = 1
                            else:
                                item_dict['isSales'] = 0

                            all_items.append(item_dict)

                        except Exception as e:
                            self.log.error(f'Tesco item error {e}')
                            continue

            except Exception as e:
                self.log.error(f'Tesco url error {e}')
                continue

        df = pd.DataFrame(all_items)
        df = df.fillna('N.a')
        df = df.loc[df['price'] != '']
        df = df[df['imageUrl'].notnull()]
        df['price'] = df['price'].astype(int)

        return df

