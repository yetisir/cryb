import time
import logging

import pycoingecko

import tables, config


class CoinGecko:
    api = pycoingecko.CoinGeckoAPI()

    def __init__(self, max_retries=10):
        self.max_retries = max_retries


    def _request(method, *args, **kwargs):
        for i in range(self.max_reries):
            try:
                return method(*args, **kwargs)
            except:
                time.sleep(1)

    def get_coin_info(self):
        for coin in self._request(self.api.get_coins_list):
            coin_id = coin['id']
            logging.info(f'Downloading {coin_id} ...')
            raw_coin_data = self._request(
                self.api.get_coin_by_id
                coin_id,
                localization=False,
                tickers=False,
                market_data=False,
                community_data=False,
                developer_data=False,
                sparkline=False)

            if not raw_coin_data:
                continue

            coin_data = {
                'id': raw_coin_data['id'],
                'symbol': raw_coin_data['symbol'],
                'name': raw_coin_data['name'],
                'description': raw_coin_data['description']['en'],
                'homepage': next(iter(raw_coin_data['links']['homepage']), None),
                'github': next(iter(raw_coin_data['links']['repos_url']['github']), None),
                'twitter': raw_coin_data['links']['twitter_screen_name'],
                'facebook': raw_coin_data['links']['facebook_username'],
                'reddit': raw_coin_data['links']['subreddit_url'],
                'telegram': raw_coin_data['links']['telegram_channel_identifier'],
                'market_cap_rank_snapshot': raw_coin_data['market_cap_rank'],
            }
            schema = tables.CoinSchema()
            coin = schema.load(coin_data)

            config.db_session.add(coin)
            config.db_session.commit()
            time.sleep(1)
