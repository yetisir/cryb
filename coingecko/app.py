import time
import logging
import asyncio

from sqlalchemy.exc import OperationalError

import config
import downloader
import apirequests


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

    loop = asyncio.get_event_loop()

    coin_gecko = downloader.Coins()

    loop = asyncio.get_event_loop()
    try:
        loop.create_task(apirequests.run())
        loop.create_task(coin_gecko.get_coins())
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()


if __name__ == '__main__':
    main()
