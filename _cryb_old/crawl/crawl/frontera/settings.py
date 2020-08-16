from __future__ import absolute_import
from frontera.settings.default_settings import MIDDLEWARES

MAX_NEXT_REQUESTS = 512
SPIDER_FEED_PARTITIONS = 2  # number of spider processes
SPIDER_LOG_PARTITIONS = 2  # worker instances
MIDDLEWARES.extend([
    'frontera.contrib.middlewares.domain.DomainMiddleware',
    'frontera.contrib.middlewares.fingerprint.DomainFingerprintMiddleware'
])

QUEUE_HOSTNAME_PARTITIONING = True
KAFKA_LOCATION = '10.0.0.223:9092'  # your Kafka broker host:port
SCORING_TOPIC = 'frontier-scoring'
URL_FINGERPRINT_FUNCTION = (
        'frontera.utils.fingerprint.hostname_local_fingerprint')

BACKEND = 'frontera.contrib.backends.remote.messagebus.MessageBusBackend'
BACKEND = 'frontera.contrib.backends.sqlalchemy.Distributed'
#BACKEND = 'backends.MongoBackend'

MAX_NEXT_REQUESTS = 2048
NEW_BATCH_DELAY = 3.0

HBASE_THRIFT_HOST = '10.0.0.223'  # HBase Thrift server host and port
HBASE_THRIFT_PORT = 9090

CRAWLING_STRATEGY = 'fourchan_strategy'
