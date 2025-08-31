import unittest
import io
import json

import riu.journal
import riu.time


class Test(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        self.maxDiff = None
        super().__init__(*args, **kwargs)

    def test_journalize(self):

        # Add entries

        s = io.StringIO()

        timestamp_dt1 = riu.time.utcnow()

        riu.journal.journalize(
            s,
            'type1',
            timestamp_dt=timestamp_dt1,
            aa='bb',
            cc='dd')

        timestamp_dt2 = riu.time.utcnow()

        riu.journal.journalize(
            s,
            'type1',
            timestamp_dt=timestamp_dt2,
            ee='ff',
            gg='hh')

        timestamp_dt3 = riu.time.utcnow()

        riu.journal.journalize(
            s,
            'type2',
            timestamp_dt=timestamp_dt3,
            ii='jj',
            kk='ll')


        # Check

        s.seek(0)

        records = [
            json.loads(line)
            for line
            in s
        ]

        expected = [
            {
                'aa': 'bb',
                'cc': 'dd',
                't': 'type1',
                't2': timestamp_dt1.isoformat(),
            },
            {
                'ee': 'ff',
                'gg': 'hh',
                't': 'type1',
                't2': timestamp_dt2.isoformat(),
            },
            {
                'ii': 'jj',
                'kk': 'll',
                't': 'type2',
                't2': timestamp_dt3.isoformat(),
            }
        ]

        self.assertEqual(records, expected)


        # Ingest using utility

        records = riu.journal.parse_journal_stream_gen(s)
        records = list(records)

        self.assertEqual(records, expected)


        # Ingest using utility (with filter)

        expected = [
            {
                'ii': 'jj',
                'kk': 'll',
                't': 'type2',
                't2': timestamp_dt3.isoformat(),
            }
        ]

        records = riu.journal.parse_journal_stream_gen(s, filter_types=['type2'])
        records = list(records)

        self.assertEqual(records, expected)


    test_parse_journal_stream = test_journalize
