from __future__ import absolute_import
from .common import *  # noqa

BACKEND = 'frontera.contrib.backends.remote.messagebus.MessageBusBackend'
KAFKA_GET_TIMEOUT = 0.5
LOCAL_MODE = False  # by default Frontera is prepared for single process mode
