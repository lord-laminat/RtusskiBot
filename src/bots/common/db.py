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
    def get_all_subscribers(self) -> list[SubscriberDTO]:
        query = 'SELECT chat_id, username, tag from subscribers'
        res = self.connection.fetchmany(query)
        return [SubscriberDTO(x) for x in res]

    def add_subscriber(self, subscriber: SubscriberDTO):
        query = 'INSERT INTO subscribers VALUES ($1, $2, $3)'
        self.connection.execute(
            query, (subscriber.chat_id, subscriber.username, subscriber.tag)
        )

    def remove_subscriber(self, subscriber):
        query = 'DELETE FROM subscribers WHERE chat_id = $1'
        self.connection.execute(query, (subscriber.chat_id))
