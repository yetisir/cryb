import time
import logging
import datetime
import asyncio

from sqlalchemy import func, desc
import pycoingecko

from ...config import config
from .. import base
from . import tables

tables.create_all()


class CoinGeckoCrawler(base.Crawler):
    api = pycoingecko.CoinGeckoAPI()
    base_url = 'https://api.coingecko.com/api/v3'

    def api_parameters(self, **parameters):
        parameter_list = [
            f'{parameter}={value}' for parameter, value in parameters.items()]
        parameter_url = '&'.join(parameter_list)
        return f'?{parameter_url}'.lower()


class Coins(CoinGeckoCrawler):
    async def get_coins(self):
        coin_list = await self.coin_list()
        # loop = asyncio.get_event_loop()
        # for coin in coin_list:
        #     loop.create_task(self.get_coin(coin))

        await asyncio.gather(*map(self.get_coin, coin_list))

        return coin_list

    async def get_coin(self, coin_id):
        if coin_id not in config.coin_ids:
            return
        coin = Coin(coin_id)
        await coin.get_info()
        # loop = asyncio.get_event_loop()
        # await coin.get_history()
        return coin.info

    async def coin_list(self):
        response = await self.request(f'{self.base_url}/coins/list')
        return [coin['id'] for coin in response if coin['id'] in config.coin_ids]


class Coin(CoinGeckoCrawler):
    def __init__(self, coin_id, **kwargs):
        super().__init__(**kwargs)

        self.coin_id = coin_id
        self.history = None
        self.raw_info = None

    async def get_history(self):
        self.history = CoinHistory(self.coin_id)
        await self.history.query()

    async def get_info(self):
        url_parameters = self.api_parameters(
            localization=False,
            tickers=False,
            market_data=False,
            community_data=False,
            developer_data=False,
            sparkline=False
        )
        url = f'{self.base_url}/coins/{self.coin_id}/{url_parameters}'
        self.raw_info = await self.request(url)

        logging.info(f'Downloaded {self.coin_id} metadata ...')
        self.save()

    def save(self):
        schema = tables.CoinSchema()
        tables.db_session.add(schema.load(self.info))
        tables.db_session.commit()

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


class CoinHistory(CoinGeckoCrawler):

    def __init__(self, coin_id, smart_scan=None, **kwargs):
        super().__init__(**kwargs)
        self.coin_id = coin_id

        if smart_scan is None:
            smart_scan = config.smart_scan
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

            if not coin_snapshot.valid_data and date != datetime.datetime.utcnow().date():
                break
            if self.smart_scan and date < max_date:
                break
            date -= date_increment

    def get_max_date(self, table):
        max_timestamp = tables.db_session.query(
            func.max(table.timestamp)).filter(table.coin_id == self.coin_id).scalar()

        return (
            datetime.datetime.fromtimestamp(max_timestamp).date() if max_timestamp
            else datetime.datetime.fromtimestamp(0).date()
        )


class CoinHistorySnapshot(CoinGeckoCrawler):
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
        return datetime.datetime(
            self.date.year, self.date.month, self.date.day).timestamp()

    @property
    def date_str(self):
        return self.date.strftime('%d-%m-%Y')

    async def query(self):

        url_parameters = self.api_parameters(
            id=self.coin_id,
            date=self.date_str,
            localization=False
        )
        url = f'{self.base_url}/coins/{self.coin_id}/history/{url_parameters}'
        self.raw_data = await self.request(url)

        logging.info(
            f'Downloaded {self.coin_id} data for {self.date_str} ...')
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
        tables.db_session.add(schema.load(self.social_data))
        tables.db_session.commit()

    def save_developer_data(self):
        if 'developer_data' not in self.raw_data.keys():
            self.valid_developer_data = False
            return
        schema = tables.CoinDeveloperDataSchema()
        tables.db_session.add(schema.load(self.developer_data))
        tables.db_session.commit()

    def save_market_data(self):
        if 'market_data' not in self.raw_data.keys():
            self.valid_market_data = False
            return
        schema = tables.CoinMarketDataSchema()
        tables.db_session.add(schema.load(self.market_data))
        tables.db_session.commit()

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
