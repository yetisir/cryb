import time
import logging

from sqlalchemy.exc import OperationalError

import config
import downloader

def main():

    # initialization loop just incase this server initializes before postgres
    try:
        config.Base.metadata.create_all(config.db_engine)
    except OperationalError:
        logging.error('Unable to connect to database. Trying again ...')
        time.sleep(1)
        main()
    except KeyboardInterrupt:
        exit()

    coin_gecko = downloader.CoinGecko()
    coin_gecko.get_coin_info()

if __name__ == '__main__':
    main()
