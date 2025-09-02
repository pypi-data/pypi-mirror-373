

import json
from dataclasses import dataclass
import arrow


@dataclass
class MachineStateChangeMessage(object):
    id: str = None
    state: str = None
    timestamp: arrow.Arrow = None

    def as_json(self):
        return json.dumps({'id': self.id, 'state': self.state,
                           'timestamp': self.timestamp.isoformat()})

    def load_dict(self, rdict):
        self.id = rdict['id']
        self.state = rdict['state']
        self.timestamp = arrow.get(rdict['timestamp'])
