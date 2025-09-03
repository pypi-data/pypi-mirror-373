

from tendril.common.exceptions.streams import JSONParseError
from tendril.common.exceptions.streams import MangledMessageError


class DataTypeNotSpecifiedError(MangledMessageError):
    def __init__(self, ctx):
        super(DataTypeNotSpecifiedError, self).__init__(ctx)

    def __repr__(self):
        return "tagDataType not found in {0}".format(self._ctx)


class DataTypeNotSupportedError(MangledMessageError):
    def __init__(self, ctx, typename):
        super(DataTypeNotSupportedError, self).__init__(ctx)
        self._typename = typename

    def __repr__(self):
        return "Unsupported tagDataType {0} found in {1}" \
               "".format(self._typename, self._ctx)


class InvalidValueError(MangledMessageError):
    def __init__(self, value, cls, ctx, inner_exc=None):
        super(MangledMessageError, self).__init__(ctx)
        self._value = value
        self._cls = cls
        self._inner_exc: Exception = inner_exc

    def __repr__(self):
        rv = "Received invalid data ({0}) for {1} in {2}".format(
            self._value, self._cls, self._ctx
        )
        if self._inner_exc:
            rv += "\n Inner Exception : {0}".format(self._inner_exc.__traceback__)
        return rv
