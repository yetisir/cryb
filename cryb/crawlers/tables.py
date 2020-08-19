import sqlalchemy as sql
from sqlalchemy.ext import declarative
from sqlalchemy.orm import relationship, sessionmaker

import marshmallow_sqlalchemy as ma

from .. import connections


db_engine = sql.create_engine(connections.postgresql())
Session = sessionmaker(bind=db_engine)
db_session = Session()
Base = declarative.declarative_base()
Base.metadata.bind = db_engine


def create_all():
    Base.metadata.create_all()


def schema_metadata(cls):
    class Meta:
        model = cls
        load_instance = True
        sqla_session = db_session
        include_fk = True
        include_relationships = True
    return Meta

# Coin Gecko Tables


class Coin(Base):
    __tablename__ = 'coin_info'

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


class CoinSocialHistory(Base):
    __tablename__ = 'coin_social_history'

    date = sql.Column(sql.Date(), primary_key=True)
    coin_id = sql.Column(sql.String(), sql.ForeignKey(
        'coin_info.id'), primary_key=True)
    facebook_likes = sql.Column(sql.Integer())
    twitter_followers = sql.Column(sql.Integer())
    reddit_average_posts_48h = sql.Column(sql.Float())
    reddit_average_comments_48h = sql.Column(sql.Float())
    reddit_subscribers = sql.Column(sql.Integer())
    reddit_accounts_active_48h = sql.Column(sql.Float())
    alexa_rank = sql.Column(sql.Integer())


class CoinSocialHistorySchema(ma.SQLAlchemyAutoSchema):
    Meta = schema_metadata(CoinSocialHistory)


class CoinDeveloperHistory(Base):
    __tablename__ = 'coin_developer_history'

    date = sql.Column(sql.Date(), primary_key=True)
    coin_id = sql.Column(sql.String(), sql.ForeignKey(
        'coin_info.id'), primary_key=True)
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


class CoinDeveloperHistorySchema(ma.SQLAlchemyAutoSchema):
    Meta = schema_metadata(CoinDeveloperHistory)


class CoinMarketHistory(Base):
    __tablename__ = 'coin_market_history'

    date = sql.Column(sql.Date(), primary_key=True)
    coin_id = sql.Column(sql.String(), sql.ForeignKey(
        'coin_info.id'), primary_key=True)
    price_usd = sql.Column(sql.Float)
    market_cap_usd = sql.Column(sql.Float)
    volume_usd = sql.Column(sql.Float)


class CoinMarketHistorySchema(ma.SQLAlchemyAutoSchema):
    Meta = schema_metadata(CoinMarketHistory)


# Forum Tables

# class Forum(Base):
#     __tablename__ = 'forum'
#     id = sql.Column(sql.String(), primary_key=True)


# class ForumSchema(ma.SQLAlchemyAutoSchema):
#     Meta = schema_metadata(Forum)


class Board(Base):
    __tablename__ = 'board'

    id = sql.Column(sql.String(), primary_key=True)
    name = sql.Column(sql.String(), nullable=False)
    description = sql.Column(sql.String())


class BoardSchema(ma.SQLAlchemyAutoSchema):
    Meta = schema_metadata(Board)


class Thread(Base):
    __tablename__ = 'thread'

    id = sql.Column(sql.String(), primary_key=True)
    board_id = sql.Column(sql.String(), sql.ForeignKey('board.id'))
    # board_id = sql.Column(sql.String(), nullable=False)
    author = sql.Column(sql.String(), nullable=False)
    title = sql.Column(sql.String(), nullable=False)
    text = sql.Column(sql.String(), nullable=False)
    created_on = sql.Column(sql.DateTime, nullable=False)
    updated_on = sql.Column(sql.DateTime, nullable=False)
    active = sql.Column(sql.Boolean, nullable=False)


class ThreadSchema(ma.SQLAlchemyAutoSchema):
    Meta = schema_metadata(Thread)


class Comment(Base):
    __tablename__ = 'comment'

    id = sql.Column(sql.String(), primary_key=True)
    thread_id = sql.Column(sql.String(), sql.ForeignKey('thread.id'))
    author = sql.Column(sql.String(), nullable=False)
    text = sql.Column(sql.String(), nullable=False)
    created_on = sql.Column(sql.DateTime, nullable=False)
    parent_comment_id = sql.Column(sql.String())


class CommentSchema(ma.SQLAlchemyAutoSchema):
    Meta = schema_metadata(Comment)
