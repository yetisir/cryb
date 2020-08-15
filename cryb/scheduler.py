from . import celery

from .config import config

from . import worker


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):

    # generating auto issuing of tokens for all lmited groups
    for destination in config.destinations:
        if destination.rate_limit:
            interval = (
                destination.rate_limit.timeframe /
                destination.rate_limit.requests
            )
            sender.add_periodic_task(
                interval,
                worker.issue_token,
                queue=f'{destination.domain}_tokens',
            )
