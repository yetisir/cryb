from celery.utils.log import get_task_logger

from .config import config
from . import worker, celery

logger = get_task_logger(__name__)


@celery.on_after_configure.connect
def setup_periodic_tasks(**kwargs):

    celery.add_periodic_task(
        1,
        worker.issue_token.signature(
            queue=f'coingecko.com_tokens'),
    )

    # # generating auto issuing of tokens for all lmited groups
    # for destination in config.destinations:
    #     logger.info(destination)
    #     if destination.rate_limit:
    #         interval = (
    #             destination.rate_limit.timeframe /
    #             destination.rate_limit.requests
    #         )
    #         celery.add_periodic_task(
    #             interval,
    #             worker.issue_token.signature(
    #                 queue=f'{destination.domain}_tokens'),
    #         )
