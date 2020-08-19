import time
import logging
import datetime
import asyncio

from sqlalchemy import func, desc

from ..config import config
from . import base
from . import tables


class CoinGeckoCrawler(base.Crawler):
    base_url = 'http://api.coingecko.com/api/v3'


class Coins(CoinGeckoCrawler):
    async def get(self):
        for target in config.targets:
            if target.domain in self.base_url:
                chunksize = target.concurrency
                break
        coin_list = await self.coin_list()
        for i in range(0, len(coin_list), chunksize):
            await self.get_coins(coin_list[i:i+chunksize])

    async def get_coins(self, coin_list):
        logging.debug(coin_list)
        coins = map(self.get_coin, coin_list)
        await asyncio.gather(*coins)

    async def get_coin(self, coin_id):
        coin = Coin(coin_id)
        await coin.get_info()
        await coin.get_history()

    async def coin_list(self):
        url_parameters = self.api_parameters(
            vs_currency='usd',
            order='market_cap_desc',
            per_page=250,
            page=1,
            sparkline=False
        )
        response = await self.request(f'{self.base_url}/coins/markets/{url_parameters}')
        return [coin['id'] for coin in response]


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

    def __init__(self, coin_id, **kwargs):
        super().__init__(**kwargs)
        self.coin_id = coin_id

    async def query(self):

        date = datetime.datetime.utcnow().date()

        date_span = date - config.timeseries_start
        all_dates = [
            date - datetime.timedelta(days=days) for
            days in range(date_span.days)]

        existing_dates = set.intersection(
            set(self.get_dates(tables.CoinSocialHistory)),
            set(self.get_dates(tables.CoinDeveloperHistory)),
            set(self.get_dates(tables.CoinMarketHistory)),
        )

        missing_dates = sorted(list(
            set(all_dates) - set(existing_dates)), reverse=True)

        for date in missing_dates:
            coin_snapshot = CoinHistorySnapshot(self.coin_id, date)
            await coin_snapshot.query()

    def get_dates(self, table):
        dates = tables.db_session.query(table.date).filter(
            table.coin_id == self.coin_id).all()

        return [date[0] for date in dates]


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

        if self.raw_data:
            logging.info(
                f'Downloaded {self.coin_id} data for {self.date_str} ...')
            self.save()
        else:
            logging.info(
                f'{self.coin_id} data for {self.date_str} does not exist...')

    def save(self):
        self.save_social_data()
        self.save_developer_data()
        self.save_market_data()

    def save_social_data(self):
        if 'community_data' not in self.raw_data.keys():
            self.valid_social_data = False
            return
        schema = tables.CoinSocialHistorySchema()
        tables.db_session.add(schema.load(self.social_data))
        tables.db_session.commit()

    def save_developer_data(self):
        if 'developer_data' not in self.raw_data.keys():
            self.valid_developer_data = False
            return
        schema = tables.CoinDeveloperHistorySchema()
        tables.db_session.add(schema.load(self.developer_data))
        tables.db_session.commit()

    def save_market_data(self):
        if 'market_data' not in self.raw_data.keys():
            self.valid_market_data = False
            return
        schema = tables.CoinMarketHistorySchema()
        tables.db_session.add(schema.load(self.market_data))
        tables.db_session.commit()

    @property
    def social_data(self):
        raw_social_data = self.raw_data.get('community_data')
        raw_public_data = self.raw_data.get('public_interest_stats')
        return {
            # 'timestamp': self.timestamp,
            'date': self.date.isoformat(),
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
            # 'timestamp': self.timestamp,
            'date': self.date.isoformat(),
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
            # 'timestamp': self.timestamp,
            'date': self.date.isoformat(),
            'coin_id': self.coin_id,
            'price_usd': raw_market_data['current_price']['usd'],
            'market_cap_usd': raw_market_data['market_cap']['usd'],
            'volume_usd': raw_market_data['total_volume']['usd'],
        }
