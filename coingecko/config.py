import logging

import pycoingecko
import sqlalchemy
from sqlalchemy.ext import declarative
from sqlalchemy.orm import sessionmaker

import os

logging.getLogger().setLevel(logging.INFO)


try:
    db_user = os.environ['POSTGRES_USER']
    db_password = os.environ['POSTGRES_PASSWORD']
    db_port = os.environ['POSTGRES_PORT']
    db_name = os.environ['POSTGRES_DB']
    db_host = os.environ['POSTGRES_HOST']
    db_uri = (
        f'postgres+psycopg2://'
        f'{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
except KeyError:
    print(
        'PostgreSQL credentials not found in ENV - setting backend as sqlite')
    db_uri = 'sqlite:///temp.sqlite'


db_engine = sqlalchemy.create_engine(db_uri)
Session = sessionmaker(bind=db_engine)
db_session = Session()
Base = declarative.declarative_base()

coin_gecko = pycoingecko.CoinGeckoAPI()
