import os
import logging
import json
import traceback
import contextlib
import shutil
import tempfile

_LOGGER = logging.getLogger(__name__)


def get_pretty_json(data):

# TODO(dustin): Add test

    return \
        json.dumps(
            data,
            sort_keys=True,
            indent=4,
            separators=(',', ': '))


def write_pretty_json(data, f):

# TODO(dustin): Add test

    json.dump(
        data,
        f,
        sort_keys=True,
        indent=4,
        separators=(',', ': '))

    f.write('\n')


def format_exception(e):

# TODO(dustin): Add test

    lines = traceback.format_exception(e.__class__, e, e.__traceback__)
    return ''.join(lines)


@contextlib.contextmanager
def temp_path():

# TODO(dustin): Add test

    original_wd = os.getcwd()

    path = tempfile.mkdtemp()
    os.chdir(path)

    try:
        yield path
    finally:
        os.chdir(original_wd)

        try:
            shutil.rmtree(path)
        except:
            pass
