from datetime import datetime
import sys
from aldi_crawler import AldiCrawler
from lidl_crawler import LidlCrawler
from auchan_crawler import AuchanCrawler
from spar_crawler import SparCrawler
from tesco_crawler import TescoCrawler
from base import Base
from functools import reduce
import pandas as pd
from pymongo import MongoClient
import smtplib
from email.message import EmailMessage
from tabulate import tabulate
import schedule
import time


class OfferLoader(Base):

    def __init__(self):
        super().__init__()

    def run_offer_crawlers(self):

        start_date = datetime.now()
        self.log.debug('Offer crawler start at: ' + str(start_date.strftime('%Y:%m:%d %H:%M:%S')))

        all_offer_df_list = []

        try:
            self.log.debug('-------Crawling Spar START---------')

            spar_crawler = SparCrawler(log=self.log, config=self.config)
            all_spar_link = spar_crawler.get_all_link_spar()
            self.log.debug(f'all_spar_link len: {len(all_spar_link)}')

            spar_offers_df = spar_crawler.get_all_offer_spar(all_spar_link)
            self.log.debug(f'spar_offers_df len: {len(spar_offers_df)}')

            all_offer_df_list.append(spar_offers_df)

            self.log.debug('-------Crawling Spar END---------')

        except Exception as e:
            self.log.error(f'Spar crawler error: {e}')

        try:
            self.log.debug('-------Crawling Aldi START---------')
            aldi_crawler = AldiCrawler(log=self.log, config=self.config)

            all_aldi_link = aldi_crawler.get_all_link_aldi()
            self.log.debug(f'all_aldi_link len: {len(all_aldi_link)}')

            aldi_offers_df = aldi_crawler.get_all_offer_aldi(all_aldi_link)
            self.log.debug(f'aldi_offers_df len: {len(aldi_offers_df)}')

            all_offer_df_list.append(aldi_offers_df)

            self.log.debug('-------Crawling Aldi END---------')

        except Exception as e:
            self.log.error(f'Aldi crawler error: {e}')

        try:
            self.log.debug('-------Crawling Lidl START---------')
            lidl_crawler = LidlCrawler(log=self.log, config=self.config)

            all_lidl_link = lidl_crawler.get_all_link_lidl()
            self.log.debug(f'all_lidl_link len: {len(all_lidl_link)}')

            lidl_offers_df = lidl_crawler.get_all_offer_lidl(all_lidl_link)
            self.log.debug(f'lidl_offers_df len: {len(lidl_offers_df)}')

            all_offer_df_list.append(lidl_offers_df)

            self.log.debug('-------Crawling Lidl END---------')

        except Exception as e:
            self.log.error(f'Lidl crawler error: {e}')

        try:
            self.log.debug('-------Crawling Auchan START---------')

            auchan_crawler = AuchanCrawler(log=self.log, config=self.config)
            token = auchan_crawler.get_auchan_token()
            all_auchan_link = auchan_crawler.get_all_auchan_link(token=token)
            self.log.debug(f'all_auchan_link len: {len(all_auchan_link)}')

            auchan_offers_df = auchan_crawler.get_all_offer_auchan(all_auchan_link=all_auchan_link, token=token)
            self.log.debug(f'auchan_offers_df len: {len(auchan_offers_df)}')

            all_offer_df_list.append(auchan_offers_df)
            self.log.debug('-------Crawling Auchan END---------')

        except Exception as e:
            self.log.error(f'Auchan crawler error: {e}')


        try:
            self.log.debug('-------Crawling Tesco START---------')
            tesco_crawler = TescoCrawler(log=self.log, config=self.config)
            all_tesco_link = tesco_crawler.get_all_tesco_link()
            self.log.debug(f'all_tesco_link len: {len(all_tesco_link)}')

            tesco_offers_df = tesco_crawler.get_all_offer_tesco(all_tesco_link)
            self.log.debug(f'tesco_offers_df len: {len(tesco_offers_df)}')

            all_offer_df_list.append(tesco_offers_df)

            self.log.debug('-------Crawling Tesco END---------')

        except Exception as e:
            self.log.error(f'Tesco crawler error {e}')

        if len(all_offer_df_list) > 0:

            self.log.debug('start concat offer dataframes...')
            all_offer_df = reduce(lambda left, right: pd.concat([left, right]), all_offer_df_list)
            self.log.debug(f'all_offer_df len: {len(all_offer_df)}')

            names = all_offer_df["itemName"]
            self.log.debug(f'duplicated offers len: '
                           f'{len(all_offer_df[names.isin(names[names.duplicated()])].sort_values("itemName"))}')

            all_offer_df = all_offer_df.drop_duplicates(subset=['itemName'], keep='first')
            self.log.debug(f'all_offer_df len after drop dupliactes: {len(all_offer_df)}')

            self.log.debug(f'sales offer len: {len(all_offer_df.loc[all_offer_df["isSales"] == 1])}')

            df_gb = all_offer_df.groupby(['shopName', 'isSales']).agg({'isSales': 'count'}).rename(
                columns={'isSales': 'count'}).reset_index()

            self.log.debug(tabulate(df_gb, headers='keys', tablefmt='psql'))

            all_offer_df['insertType'] = 'automate'

            now = datetime.now()
            time_key = now.strftime("%Y_%m_%d_%H_%M")
            self.log.debug(f'time_key to current load {time_key}')
            all_offer_df['timeKey'] = time_key

            self.load_data_to_mongo(all_offer_df)

            end_date = datetime.now()

            self.log.debug('Offer crawler start at: ' + str(end_date.strftime('%Y:%m:%d %H:%M:%S')))
            diff = end_date - start_date
            self.log.debug(f'Total run time: {round(diff.total_seconds() / 60 , 2)} minutes')

            self.send_mail(time_key, df_gb)


        else:
            self.log.debug(f'all_offer_df_list len is empty exiting!')

    def load_data_to_mongo(self, all_offer_df):
        self.log.debug(f'load_data_to_mongo invoked!')

        user_name = self.config.get('DB', 'user_name')
        password = self.config.get('DB', 'password')
        host = self.config.get('DB', 'host')
        mongo_url = f'mongodb://{user_name}:{password}{host}'
        collection_name = self.config.get('DB', 'collection_name')
        client = MongoClient(mongo_url)
        db = client['offer']
        offer_collection = db[collection_name]

        data_dict = all_offer_df.to_dict("records")

        mongo_result = offer_collection.insert_many(data_dict)

        self.log.debug(f'inserted mongo len: {len(mongo_result.inserted_ids)}')

    def send_mail(self, time_key, df_gb):

        self.log.info('send mail invoked!')

        msg = EmailMessage()
        my_address = self.config.get('MAIL', 'my_address')
        app_generated_password = self.config.get('MAIL', 'app_generated_password')

        msg["Subject"] = 'Hot deals offer crawler - ' + time_key
        msg["From"] = my_address
        msg["To"] = self.config.get('MAIL', 'mail_to')

        message_text = self.config.get('MAIL', 'message_text')

        msg.set_content(f'{message_text} \n {tabulate(df_gb, headers="keys", tablefmt="psql")}')

        '''
        if len(file_to_attach_list) > 0:

            for file_name in file_to_attach_list:
                with open(file_name, "rb") as file:  # open image file
                    file_data = file.read()
                    msg.add_attachment(file_data, maintype="application", subtype="xlsx", filename=file_name)
                    
        '''

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(my_address, app_generated_password)  # login gmail account

            self.log.info("sending mail")
            smtp.send_message(msg)  # send message
            self.log.info("mail has sent")

if __name__ == "__main__":
    try:

        offer_loader = OfferLoader()
        #all_offer_df_list = offer_loader.run_offer_crawlers()

        #schedule.every(0.5).minutes.do(offer_loader.run_offer_crawlers)
        schedule.every().day.at("21:16").do(offer_loader.run_offer_crawlers)

        while True:
            schedule.run_pending()
            time.sleep(1)

    except Exception as e:
        print('main exception :' + str(e))
        sys.exit(1)






