from __future__ import absolute_import
from .common import *  # noqa

BACKEND = 'frontera.contrib.backends.hbase.HBaseBackend'

MAX_NEXT_REQUESTS = 2048
NEW_BATCH_DELAY = 3.0

HBASE_THRIFT_HOST = 'localhost'  # HBase Thrift server host and port
HBASE_THRIFT_PORT = 9090
