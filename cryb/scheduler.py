from celery.utils.log import get_task_logger

from .config import config
from . import worker, celery

logger = get_task_logger(__name__)


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    for target in config.targets:
        if target.rate_limit:
            interval = (
                target.rate_limit.timeframe /
                target.rate_limit.requests
            )
            sender.add_periodic_task(
                interval,
                worker.issue_token.signature(
                    queue=f'{target.domain}_tokens'),
                name=target.domain,
            )
