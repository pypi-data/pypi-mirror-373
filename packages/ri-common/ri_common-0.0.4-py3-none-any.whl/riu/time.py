import datetime

import dateutil.tz


def utcnow(round=False):

    now_dt = \
        datetime.datetime.utcnow().replace(
            tzinfo=dateutil.tz.UTC)

    if round is True:
        now_dt -= datetime.timedelta(microseconds=now_dt.microsecond)

    return now_dt
