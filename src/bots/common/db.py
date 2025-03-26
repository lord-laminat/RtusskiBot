from abc import ABC

import asyncpg

from bots.common.models import SubscriberDTO


class BaseSubscriberRepo(ABC):
    def __init__(self, conn):
        self.connection = conn

    def get_all_subscribers(self):
        return NotImplemented

    def add_subscriber(self, subscriber: SubscriberDTO):
        return NotImplemented

    def remove_subscriber(self, subscriber: SubscriberDTO):
        return NotImplemented


class PostgresSubscriberRepo(BaseSubscriberRepo):
    def get_all_subscribers(self):
        query = 'SELECT chat_id, username, tag from subscribers'
        res = self.connection.fetchmany(query)
        return [SubscriberDTO(x) for x in res]
