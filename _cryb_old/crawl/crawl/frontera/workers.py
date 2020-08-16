from __future__ import absolute_import
from .common import *  # noqa

BACKEND = 'frontera.contrib.backends.sqlalchemy.Distributed'

MAX_NEXT_REQUESTS = 2048
NEW_BATCH_DELAY = 3.0

SQLALCHEMYBACKEND_ENGINE = 'postgres:///10.0.0.223:5432'
