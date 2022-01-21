from dataclasses import dataclass
from common import Model

@dataclass
class RedirectionMapModel(Model):
    __mapping__ = {
        'id': 'id',
        'key': 'key',
        'value': 'value',
        'user_id': 'userId'
    }

    id: str
    key: str
    value: str
    user_id: str
