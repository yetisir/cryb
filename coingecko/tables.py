import sqlalchemy as sql
from sqlalchemy.ext import declarative
from sqlalchemy.orm import relationship
import marshmallow_sqlalchemy as ma

import config


def schema_metadata(cls):
    class Meta:
        model = cls
        load_instance=True
        sqla_session = config.db_session
        include_fk = True
        include_relationships = True
    return Meta


class Coin(config.Base):
    __tablename__ = 'coin'

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
    Meta = schema_metadata(Coin)


class CoinSocialData(config.Base):
    __tablename__ = 'coin_social_data'

    timestamp = sql.Column(sql.Date(), primary_key=True)
    coin_id = sql.Column(sql.String(), sql.ForeignKey('coin.id'), primary_key=True)
    facebook_likes = sql.Column(sql.Integer(), nullable=False)
    twitter_followers = sql.Column(sql.Integer(), nullable=False)
    reddit_average_posts_48h = sql.Column(sql.Float(), nullable=False)
    reddit_avergage_comments_48h = sql.Column(sql.Float(), nullable=False)
    reddit_subscribers = sql.Column(sql.Integer(), nullable=False)
    reddit_accounts_active_48h = sql.Column(sql.Float(), nullable=False)


class CoinSocialDataSchema(ma.SQLAlchemyAutoSchema):
    Meta = schema_metadata(CoinSocialData)


class CoinDeveloperData(config.Base):
    __tablename__ = 'coin_developer_data'

    timestamp = sql.Column(sql.Date(), primary_key=True)
    coin_id = sql.Column(sql.String(), sql.ForeignKey('coin.id'), primary_key=True)
    forks = sql.Column(sql.Integer(), nullable=False)
    stars = sql.Column(sql.Integer(), nullable=False)
    subscribers = sql.Column(sql.Integer(), nullable=False)
    total_issues = sql.Column(sql.Integer(), nullable=False)
    closed_issues = sql.Column(sql.Integer(), nullable=False)
    pull_requests_merged = sql.Column(sql.Integer(), nullable=False)
    pull_request_contributors = sql.Column(sql.Integer(), nullable=False)
    code_additions_4_weeks = sql.Column(sql.Float(), nullable=False)
    code_deletions_4_weeks = sql.Column(sql.Float(), nullable=False)
    commit_count_4_weeks = sql.Column(sql.Float(), nullable=False)


class CoinDeveloperDataSchema(ma.SQLAlchemyAutoSchema):
    Meta = schema_metadata(CoinDeveloperData)


class CoinPublicInterestData(config.Base):
    __tablename__ = 'coin_public_interest_data'

    timestamp = sql.Column(sql.Date(), primary_key=True)
    coin_id = sql.Column(sql.String(), sql.ForeignKey('coin.id'), primary_key=True)
    alexa_rank = sql.Column(sql.Integer(), nullable=False)
    bing_matches = sql.Column(sql.Integer(), nullable=False)


class CoinPublicInterestDataSchema(ma.SQLAlchemyAutoSchema):
    Meta = schema_metadata(CoinPublicInterestData)


class CoinMarketData(config.Base):
    __tablename__ = 'coin_market_data'

    timestamp = sql.Column(sql.Date(), primary_key=True)
    coin_id = sql.Column(sql.String(), sql.ForeignKey('coin.id'), primary_key=True)
    price_usd = sql.Column(sql.Float, nullable=False)


class CoinMarketDataSchema(ma.SQLAlchemyAutoSchema):
    Meta = schema_metadata(CoinMarketData)
