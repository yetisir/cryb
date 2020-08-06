import time
import logging
import datetime
import asyncio

from sqlalchemy import func, desc

import tables
import config
import utils
import apirequests


class Coins:
    # @utils.scheduler('1w')
    async def get_coins(self):
        coin_list = await self.coin_list()
        asyncio.gather(*map(self.get_coin, coin_list))
        # async for coin in self.coin_list():
        #     coin_id = coin['id']
        #     # temp
        #     if coin_id not in config.settings['coin_ids']:
        #         continue
        #     coin = Coin(coin_id)

        #     await coin.get_info()
        #     await coin.get_history()

    async def get_coin(self, coin_id):

        # temp
        if coin_id not in config.settings['coin_ids']:
            return

        print(coin_id, 1)

        coin = Coin(coin_id)
        # await coin.get_info()
        print(coin_id, 2)
        await coin.get_history()
        print(coin_id, 2)

    async def coin_list(self):
        response = await apirequests.add('get_coins_list')

        return [coin['id'] for coin in response]


class Coin:

    def __init__(self, coin_id, **kwargs):
        super().__init__(**kwargs)

        self.coin_id = coin_id
        self.history = None
        self.raw_info = None

    async def get_history(self):
        print(self.coin_id)
        self.history = CoinHistory(self.coin_id)
        await self.history.query()

    async def get_info(self):
        logging.info(f'Downloading {self.coin_id} metadata ...')
        self.raw_info = await apirequests.add(
            'get_coin_by_id',
            self.coin_id,
            localization=False,
            tickers=False,
            market_data=False,
            community_data=False,
            developer_data=False,
            sparkline=False)

        self.save()

    def save(self):
        schema = tables.CoinSchema()
        config.db_session.add(schema.load(self.info))
        config.db_session.commit()

    @property
    def info(self):
        return {
            'id': self.coin_id,
            'symbol': self.symbol,
            'name': self.name,
            'description': self.description,
            'homepage': self.homepage,
            'github': self.github_repo,
            'twitter': self.twitter_handle,
            'facebook': self.facebook_username,
            'reddit': self.subreddit,
            'telegram': self.telegram_channel,
            'market_cap_rank_snapshot': self.market_cap_rank,
        }

    @property
    def symbol(self):
        return self.raw_info['symbol']

    @property
    def name(self):
        return self.raw_info['name']

    @property
    def description(self):
        return self.raw_info['description']['en']

    @property
    def market_cap_rank(self):
        return self.raw_info['market_cap_rank']

    @property
    def homepage(self):
        homepage = next(iter(self.raw_info['links']['homepage']), None)
        return homepage.lower() if homepage else None

    @property
    def telegram_channel(self):
        telegram_channel = (
            self.raw_info['links']['telegram_channel_identifier']
        )
        return telegram_channel.lower() if telegram_channel else None

    @property
    def github_repo(self):
        github_repo = next(
            iter(self.raw_info['links']['repos_url']['github']), None)
        return (
            github_repo.split('github.com/')[-1].lower() if github_repo
            else None
        )

    @property
    def facebook_username(self):
        facebook_username = self.raw_info['links']['facebook_username']
        return (
            facebook_username.lower() if facebook_username else None
        )

    @property
    def subreddit(self):
        subreddit_url = self.raw_info['links']['subreddit_url']
        return (
            subreddit_url.split('/r/')[-1].strip('/').lower() if subreddit_url
            else None
        )

    @property
    def twitter_handle(self):
        twitter_handle = self.raw_info['links']['twitter_screen_name']
        return twitter_handle.lower() if twitter_handle else None


class CoinHistory:

    def __init__(self, coin_id, smart_scan=None, **kwargs):
        super().__init__(**kwargs)
        self.coin_id = coin_id

        if smart_scan is None:
            smart_scan = config.settings['smart_scan']
        self.smart_scan = smart_scan

    async def query(self):

        date = datetime.datetime.utcnow().date()
        date_increment = datetime.timedelta(days=1)

        max_date = min(
            self.get_max_date(tables.CoinDeveloperData),
            self.get_max_date(tables.CoinSocialData),
        )

        while True:
            coin_snapshot = CoinHistorySnapshot(self.coin_id, date)
            await coin_snapshot.query()

            if not coin_snapshot.valid_data:
                break
            if self.smart_scan and date < max_date:
                break
            date -= date_increment

    def get_max_date(self, table):
        max_timestamp = config.db_session.query(
            func.max(table.timestamp)).filter(table.coin_id == self.coin_id).scalar()

        return (
            datetime.datetime.fromtimestamp(max_timestamp).date() if max_timestamp
            else datetime.datetime.fromtimestamp(0).date()
        )


class CoinHistorySnapshot:
    def __init__(self, coin_id, date, **kwargs):
        super().__init__(**kwargs)
        self.coin_id = coin_id
        self.date = date

        self.valid_social_data = True
        self.valid_developer_data = True
        self.valid_market_data = True

    @property
    def valid_data(self):
        if (
            self.valid_developer_data or
            self.valid_social_data or
            self.valid_market_data
        ):
            return True
        else:
            return False

    @property
    def timestamp(self):
        return (
            datetime.datetime(self.date.year, self.date.month, self.date.day) +
            datetime.timedelta(days=1, microseconds=-1)
        ).timestamp()

    @property
    def date_str(self):
        return self.date.strftime('%d-%m-%Y')

    async def query(self):
        logging.info(
            f'Downloading {self.coin_id} data for {self.date_str} ...')
        self.raw_data = await apirequests.add(
            'get_coin_history_by_id',
            id=self.coin_id,
            date=self.date_str,
            localization=False,
        )
        self.save()

    def save(self):
        self.save_social_data()
        self.save_developer_data()
        self.save_market_data()

    def save_social_data(self):
        if 'community_data' not in self.raw_data.keys():
            self.valid_social_data = False
            return
        schema = tables.CoinSocialDataSchema()
        config.db_session.add(schema.load(self.social_data))
        config.db_session.commit()

    def save_developer_data(self):
        if 'developer_data' not in self.raw_data.keys():
            self.valid_developer_data = False
            return
        schema = tables.CoinDeveloperDataSchema()
        config.db_session.add(schema.load(self.developer_data))
        config.db_session.commit()

    def save_market_data(self):
        if 'market_data' not in self.raw_data.keys():
            self.valid_market_data = False
            return
        schema = tables.CoinMarketDataSchema()
        config.db_session.add(schema.load(self.market_data))
        config.db_session.commit()

    @property
    def social_data(self):
        raw_social_data = self.raw_data.get('community_data')
        raw_public_data = self.raw_data.get('public_interest_stats')
        return {
            'timestamp': self.timestamp,
            'date': self.date_str,
            'coin_id': self.coin_id,
            'facebook_likes': raw_social_data['facebook_likes'],
            'twitter_followers': raw_social_data['twitter_followers'],
            'reddit_average_posts_48h': raw_social_data['reddit_average_posts_48h'],
            'reddit_average_comments_48h': raw_social_data['reddit_average_comments_48h'],
            'reddit_subscribers': raw_social_data['reddit_subscribers'],
            'reddit_accounts_active_48h': raw_social_data['reddit_accounts_active_48h'],
            'alexa_rank': raw_public_data['alexa_rank'],
        }

    @property
    def developer_data(self):
        raw_developer_data = self.raw_data.get('developer_data')
        return {
            'timestamp': self.timestamp,
            'date': self.date_str,
            'coin_id': self.coin_id,
            'forks': raw_developer_data['forks'],
            'stars': raw_developer_data['stars'],
            'subscribers': raw_developer_data['subscribers'],
            'total_issues': raw_developer_data['total_issues'],
            'closed_issues': raw_developer_data['closed_issues'],
            'pull_requests_merged': raw_developer_data['pull_requests_merged'],
            'pull_request_contributors': raw_developer_data['pull_request_contributors'],
            'code_additions_4_weeks': raw_developer_data['code_additions_deletions_4_weeks']['additions'],
            'code_deletions_4_weeks': raw_developer_data['code_additions_deletions_4_weeks']['deletions'],
            'commit_count_4_weeks': raw_developer_data['commit_count_4_weeks'],
        }

    @property
    def market_data(self):
        raw_market_data = self.raw_data.get('market_data')
        return {
            'timestamp': self.timestamp,
            'date': self.date_str,
            'coin_id': self.coin_id,
            'price_usd': raw_market_data['current_price']['usd'],
            'market_cap_usd': raw_market_data['market_cap']['usd'],
            'volume_usd': raw_market_data['total_volume']['usd'],
        }
