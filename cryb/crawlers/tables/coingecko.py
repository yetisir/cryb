import marshmallow_sqlalchemy as ma
import sqlalchemy as sql

from .common import Database


class Coin(Database.Table):
    __tablename__ = 'coingecko_coin'

    id = sql.Column(sql.String(), primary_key=True)
    symbol = sql.Column(sql.String(), nullable=False)
    name = sql.Column(sql.String(), nullable=False)
    market_cap_rank_snapshot = sql.Column(sql.Integer())
    description = sql.Column(sql.String())
    homepage = sql.Column(sql.String())
    github = sql.Column(sql.String())
    twitter = sql.Column(sql.String())
    facebook = sql.Column(sql.String())
    reddit = sql.Column(sql.String())
    telegram = sql.Column(sql.String())


class CoinSchema(ma.SQLAlchemyAutoSchema):
    Meta = Database.schema_metadata(Coin)


class SocialHistory(Database.Table):
    __tablename__ = 'coingecko_social_history'

    date = sql.Column(sql.Date(), primary_key=True)
    coin_id = sql.Column(sql.String(), sql.ForeignKey(
        'coingecko_coin.id'), primary_key=True)
    facebook_likes = sql.Column(sql.Integer())
    twitter_followers = sql.Column(sql.Integer())
    reddit_average_posts_48h = sql.Column(sql.Float())
    reddit_average_comments_48h = sql.Column(sql.Float())
    reddit_subscribers = sql.Column(sql.Integer())
    reddit_accounts_active_48h = sql.Column(sql.Float())
    alexa_rank = sql.Column(sql.Integer())


class SocialHistorySchema(ma.SQLAlchemyAutoSchema):
    Meta = Database.schema_metadata(SocialHistory)


class DeveloperHistory(Database.Table):
    __tablename__ = 'coingecko_developer_history'

    date = sql.Column(sql.Date(), primary_key=True)
    coin_id = sql.Column(sql.String(), sql.ForeignKey(
        'coingecko_coin.id'), primary_key=True)
    forks = sql.Column(sql.Integer())
    stars = sql.Column(sql.Integer())
    subscribers = sql.Column(sql.Integer())
    total_issues = sql.Column(sql.Integer())
    closed_issues = sql.Column(sql.Integer())
    pull_requests_merged = sql.Column(sql.Integer())
    pull_request_contributors = sql.Column(sql.Integer())
    code_additions_4_weeks = sql.Column(sql.Float())
    code_deletions_4_weeks = sql.Column(sql.Float())
    commit_count_4_weeks = sql.Column(sql.Float())


class DeveloperHistorySchema(ma.SQLAlchemyAutoSchema):
    Meta = Database.schema_metadata(DeveloperHistory)


class MarketHistory(Database.Table):
    __tablename__ = 'coingecko_market_history'

    date = sql.Column(sql.Date(), primary_key=True)
    coin_id = sql.Column(sql.String(), sql.ForeignKey(
        'coingecko_coin.id'), primary_key=True)
    price_usd = sql.Column(sql.Float)
    market_cap_usd = sql.Column(sql.Float)
    volume_usd = sql.Column(sql.Float)


class MarketHistorySchema(ma.SQLAlchemyAutoSchema):
    Meta = Database.schema_metadata(MarketHistory)
