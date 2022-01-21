from logging import Logger
import re
from flask import redirect
from common import Controller
from common.cache import Cache, cached
from common.databases.nosql import DatabaseOperations
from common.databases.errors import RecordNotFound
from common import http_responses
from redirection_map_model import RedirectionMapModel

class RedirectionController(Controller):

    _cache: Cache
    _database_op: DatabaseOperations

    def __init__(self, logger: Logger, cache: Cache, database_op: DatabaseOperations):
        super().__init__(logger)
        self._cache = cache
        self._database_op = database_op

    def _get_cached(self, key) -> str:
        @cached(self._cache)
        def wrapper(key):
            db_entry = self._database_op.get({'key': key}, '0')
            data = db_entry.data
            data['id'] = db_entry.id
            redirection = RedirectionMapModel.from_dict(RedirectionMapModel, data)
            return redirection.value
        return wrapper(key)

    def get(self, path):
        path = f'/{path}'
        try:
            target = self._get_cached(path)
        except RecordNotFound as e:
            self._logger.exception(e)
            return http_responses.NotFoundResponse()
        return redirect(target)