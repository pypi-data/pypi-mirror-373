

import arrow


def timestamp_to_utc(ts):
    local_timestamp = arrow.get(ts)
    return local_timestamp.to('UTC')