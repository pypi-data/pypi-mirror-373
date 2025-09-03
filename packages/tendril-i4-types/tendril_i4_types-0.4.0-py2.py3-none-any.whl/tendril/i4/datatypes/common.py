# encoding: utf-8

import arrow
import datetime
from ..formats.timestamps import timestamp_to_utc


class BaseDataPoint(object):
    def __init__(self, received_dict):
        self._measurement = None
        self._localizers = {}
        self._datatype = None
        self._value = None
        self._timestamp = None
        self.original = received_dict
        self._load_from_dict(received_dict)

    @property
    def value(self):
        return self._value

    @property
    def hr_value(self):
        return self._value

    @property
    def timestamp(self) -> arrow.Arrow:
        return self._timestamp

    @property
    def datatype(self):
        return self._datatype

    @property
    def measurement(self):
        return self._measurement

    @property
    def localizers(self):
        return self._localizers

    @property
    def channel_id(self):
        return (self._measurement,
                *[self._localizers[k] for k in self._localizer_keys])

    @property
    def _localizer_keys(self):
        return ['equipmentName']

    @property
    def routing_key(self):
        localizers = ".".join([self._localizers[k] for k in self._localizer_keys])
        return f"{localizers}.{self.measurement}"

    def _load_from_dict(self, received_dict):
        self._measurement = received_dict['tagName'].replace(' ', '')
        if 'tagTimestamp' in received_dict:
            self._timestamp = timestamp_to_utc(received_dict['tagTimestamp'])
        else:
            self._timestamp = datetime.datetime.now(datetime.UTC)
        self._localizers = {k: received_dict[k] for k in self._localizer_keys}
        self._datatype = received_dict['tagDataType']

    @property
    def suggested_processors(self):
        return self._suggested_processors()

    @staticmethod
    def _suggested_processors():
        return []

    def __getattr__(self, item):
        if item in self._localizer_keys:
            return self._localizers[item]

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return self._value == other.value
        else:
            raise ValueError("Cannot compare datapoints of different classes, "
                             "got {} and {}".format(self.__class__,
                                                    other.__class__))

    def __ne__(self, other):
        if self.__class__ == other.__class__:
            return self._value != other.value
        else:
            raise ValueError("Cannot compare datapoints of different classes, "
                             "got {} and {}".format(self.__class__,
                                                    other.__class__))
