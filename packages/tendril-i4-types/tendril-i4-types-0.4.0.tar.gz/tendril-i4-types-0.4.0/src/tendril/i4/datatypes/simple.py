# encoding: utf-8

# Copyright (C) 2021 Neel Aundhia, IIT Kanpur
#               2021 Chintalagiri Shashank, IIT Kanpur
#
# This file is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from numbers import Number
from decimal import Decimal

from .common import BaseDataPoint
from tendril.i4.exceptions import InvalidValueError
from tendril.stream.processors.rlc import RunLengthProcessor


class SimpleDataPoint(BaseDataPoint):
    _objclass = None

    def _load_from_dict(self, received_dict):
        super(SimpleDataPoint, self)._load_from_dict(received_dict)
        value = received_dict['tagValue']
        parse_exception = None
        if not isinstance(value, self._objclass):
            try:
                value = self._objclass(value)
            except Exception as e:
                parse_exception = e
        if not isinstance(value, self._objclass):
            raise InvalidValueError(received_dict['tagValue'],
                                    self.__class__.__name__,
                                    received_dict,
                                    parse_exception)
        self._value = value

    def _suggested_processors(self):
        rv = [RunLengthProcessor]
        rv.extend(super(SimpleDataPoint, self)._suggested_processors())
        return rv


class BooleanDataPoint(SimpleDataPoint):
    _objclass = bool


class NumericDataPoint(SimpleDataPoint):
    _objclass = Number


class IntegerDataPoint(NumericDataPoint):
    _objclass = int


class DecimalDataPoint(NumericDataPoint):
    _objclass = Decimal


class StringDataPoint(SimpleDataPoint):
    _objclass = str

    @property
    def _formatted_value(self):
        return '"{}"'.format(self._value)
