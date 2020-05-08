import pycoingecko

import tables, config


class CoinGecko:
    def __init__(self):
        self.api = pycoingecko.CoinGeckoAPI()

    def get_coin_info():
        for coin in icg.get_coins_list():
            raw_coin_data = cg.get_coin_by_id(coin['id'])
            coin_data = {
                'id': raw_coin_data['id'],
                'symbol': raw_coin_data['symbol'],
                'name': raw_coin_data['name'],
                'description': raw_coin_data['description']['en'],
                'homepage': raw_coin_data['links']['homepage'][0],
                'github': raw_coin_data['links']['repos_url']['github'][0],
                'twitter': raw_coin_data['links']['twitter_screen_name'],
                'facebook': raw_coin_data['links']['facebook_username'],
                'reddit': raw_coin_data['links']['subreddit_url'],
                'telegram': raw_coin_data['links']['telegram_channel_identifier'],
            }
            schema = tables.CoinSchema()
            coin = schema.load(coin_data)

            config.session.add(coin)

