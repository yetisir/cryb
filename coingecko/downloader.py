import time
import logging

import pycoingecko

import tables, config  # , utils


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

    #@utils.scheduler('1w')
    def get_coin_info(self):
        for coin in self._request(self.api.get_coins_list):

            coin_id = coin['id']

            # temp
            if coin_id not in [
                'bitcoin', 'ethereum', 'ripple', 'tether', 'bitcoin-cash', 'bitcoin-cash-sv', 'litecoin', 'eos', 'binancecoin', 'tezos']:
                continue

            #
            logging.info(f'Downloading {coin_id} ...')
            raw_coin_data = self._request(
                self.api.get_coin_by_id,
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

    def get_developer_history(self, date, coin_id, data):
        raw_history_data = data.get('developer_data')
        if not raw_history_data:
            return

        history_data = {
            'timestamp': date.timestamp(),
            'coin_id': coin_id,
            'forks': raw_history_data['forks'],
            'start': raw_history_data['start'],
            'subscribers': raw_history_data['subscribers'],
            'total_issues': raw_history_data['total_issues'],
            'closed_issues': raw_history_data['closed_issues'],
            'pull_requests_merged': raw_history_data['pull_requests_merged'],
            'pull_requests_contributed': raw_history_data['pull_requests_contributed'],
            'code_additions_4_weeks': raw_history_data['code_additions_4_weeks'],
            'code_deletions_4_weeks': raw_history_data['code_deletions_4_weeks'],
            'commit_count_4_weeks': raw_history_data['commit_count_4_weeks'],
        }

        schema = tables.CoinSocialDataSchema()
        history = schema.load(history_data)

        config.db_session.add(history)
        config.db_session.commit()


    def get_social_history(self, date, coin_id, data):
        raw_history_data = data.get('community_data')
        if not raw_history_data:
            return

        social_history_data = {
            'timestamp': date.timestamp(),
            'coin_id': coin_id,
            'facebook_likes': raw_history_data['facebook_likes'],
            'twitter_followers': raw_history_data['twitter_followers'],
            'reddit_average_posts_48h': raw_history_data['reddit_average_posts_48h'],
            'reddit_average_comments_48h': raw_history_data['reddit_average_comments_48h'],
            'reddit_subscribers': raw_history_data['reddit_subscribers'],
            'reddit_accounts_active_48h': raw_history_data['reddit_accounts_active_48h'],
        }

        schema = tables.CoinSocialDataSchema()
        social_history = schema.load(social_history_data)

        config.db_session.add(social_history)
        config.db_session.commit()

    def get_max_date(self, table):
        max_timestamp = table.query.func.max(table.timestamp)
        return datetime.datetime.fromtimestamp(max_timestamp)

    def get_coin_history(self, coin_id):

        date = datetime.date()
        increment = datetime.timedelta(days=1)
        query_previous_day = True

        max_social_data_date = self.get_max_date(tables.CoinSocialData)
        max_developer_data_date = self.get_max_date(tables.CoinDeveloperData)
        max_public_interest_data_date = None

        while query_previous_day:
            date_str = date.strftime('%d-%m-%Y')
            coin = self.api.get_coin_history_by_id(id=coin_id, date=date, localization=false)

            self.get_social_history(coin_id, coin)


    def get_all_coin_history(self, num_coins=10):
        coins = config.db_session.query(
            tables.Coin.query
            .order_by(tables.Coin.market_cap_rank_snapshot)
            .limit(num_coins)
        )

        for coin in coins:
            self.get_coin_history(self, coin['id'])
