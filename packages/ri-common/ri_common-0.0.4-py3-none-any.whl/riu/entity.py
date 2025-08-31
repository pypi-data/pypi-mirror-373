import logging

_LOGGER = logging.getLogger(__name__)


class BaseEntity(object):
    def __init__(self, data):
        self._data = data

    @property
    def data(self):
        return self._data

    @property
    def id(self):
        raise NotImplementedError()

    @property
    def id_attribute_name(self):
        return 'id'
