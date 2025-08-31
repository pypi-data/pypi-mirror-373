import logging
import json

import riu.time

_LOGGER = logging.getLogger(__name__)


def journalize(resource, type_=None, timestamp_dt=None, **kwargs):

    if timestamp_dt is None:
        timestamp_dt = riu.time.utcnow()

    info = {
        't2': timestamp_dt.isoformat(),
    }

    if type_ is not None:
        info['t'] = type_

    info.update(kwargs)

    json.dump(info, resource)
    resource.write('\n')


def parse_journal_stream_gen(s, filter_types=None):

    s.seek(0)

    journal_entries = (
        json.loads(line)
        for line
        in s
    )

    if filter_types:
        journal_entries = (
            record
            for record
            in journal_entries
            if record['t'] in filter_types
        )

    yield from journal_entries
