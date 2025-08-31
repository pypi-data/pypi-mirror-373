import unittest

import dateutil.tz

import riu.time


class Test(unittest.TestCase):
    def test_utcnow(self):

        dt = riu.time.utcnow()
        self.assertEqual(dt.tzinfo, dateutil.tz.UTC)
