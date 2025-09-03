

import json
from datetime import datetime
from dataclasses import dataclass
import arrow

from .timestamps import timestamp_to_utc


class ServicePingMessage(object):
    def __init__(self, key=None, received_dict=None, service_name=None):
        self._channel_id = None
        self._timestamp = None
        if key:
            self._load_from_routing_key(key)
        else:
            self._channel_id = service_name
        if received_dict:
            self._load_from_dict(received_dict)
        else:
            self._timestamp = timestamp_to_utc(datetime.now())

    @property
    def channel_id(self):
        return self._channel_id

    @property
    def timestamp(self):
        return self._timestamp

    def _load_from_routing_key(self, key):
        # assert key.rsplit('.', 1)[1] == 'ping'
        # assert key.split('.', 1)[0] == 'system'
        self._channel_id = key.split('.', 1)[1].rsplit('.', 1)[0]

    def _load_from_dict(self, received_dict):
        self._timestamp = timestamp_to_utc(received_dict['timeStamp'])

    def as_json(self):
        value = "Construct here"
        return value


@dataclass
class ServiceStateChangeMessage(object):
    id: str = None
    state: bool = False
    timestamp: arrow.Arrow = None

    def as_json(self):
        return json.dumps({'id': self.id, 'state': self.state,
                           'timestamp': self.timestamp.isoformat()})

    def load_dict(self, rdict):
        self.id = rdict['id']
        self.state = rdict['state']
        self.timestamp = arrow.get(rdict['timestamp'])
