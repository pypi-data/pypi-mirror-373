# encoding: utf-8

# Copyright (C) 2021 Neel Aundhia, IIT Kanpur
#               2021 Chintalagiri Shashank, IIT Kanpur
#
# This file is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from .common import BaseDataPoint
from tendril.i4.exceptions import InvalidValueError
from tendril.stream.processors.rlc import RunLengthProcessor


operational_status = {
    0: "offline",
    1: "emergency_signal",
    2: "fault_alarm",
    3: "idle",
    4: "operational_manual",
    5: "operational_auto",
}


class OperationalStatusDataPoint(BaseDataPoint):
    def _load_from_dict(self, received_dict):
        super(OperationalStatusDataPoint, self)._load_from_dict(received_dict)
        for key, value in operational_status.items():
            if value == received_dict['tagValue']:
                self._value = key
                break
        else:
            raise InvalidValueError(received_dict['tagValue'],
                                    self.__class__.__name__,
                                    received_dict)

    def _suggested_processors(self):
        rv = [RunLengthProcessor]
        rv.extend(super(OperationalStatusDataPoint, self)._suggested_processors())
        return rv

    @property
    def hr_value(self):
        return operational_status[self._value]
