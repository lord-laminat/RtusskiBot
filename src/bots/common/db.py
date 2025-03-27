from abc import ABC, abstractmethod

from bots.common.models import SubscriberDTO, UserDTO


class BaseSubscriberRepo(ABC):
    def __init__(self, conn):
        self.connection = conn

    @abstractmethod
    async def get_all_subscribers(self) -> list[SubscriberDTO]:
        pass

    @abstractmethod
    async def add_subscriber(self, subscriber: SubscriberDTO):
        pass

    @abstractmethod
    async def remove_subscriber(self, subscriber: SubscriberDTO) -> None:
        pass

    @abstractmethod
    async def get_subscriber(self, chat_id) -> SubscriberDTO:
        pass


class BaseUserRepo(ABC):
    def __init__(self, conn):
        self.connection = conn

    @abstractmethod
    async def add_user(self, user: UserDTO) -> None:
        pass

    @abstractmethod
    async def get_all_users(self) -> list[UserDTO]:
        pass

    @abstractmethod
    async def get_user(self, chat_id: int) -> UserDTO:
        pass


class PostgresSubscriberRepo(BaseSubscriberRepo):
    async def get_all_subscribers(self) -> list[SubscriberDTO]:
        query = 'SELECT chat_id, username, tag from subscribers;'
        res = self.connection.fetchmany(query)
        return [SubscriberDTO(x[0], x[1]) for x in res]

    async def add_subscriber(self, subscriber: SubscriberDTO):
        query = 'INSERT INTO subscribers VALUES ($1, $2, $3);'
        await self.connection.execute(
            query, (subscriber.chat_id, subscriber.username)
        )

    async def remove_subscriber(self, subscriber):
        query = 'DELETE FROM subscribers WHERE chat_id = $1;'
        await self.connection.execute(query, (subscriber.chat_id))

    async def get_subscriber(self, chat_id) -> SubscriberDTO:
        query = 'SELECT chat_id, username FROM subscribers WHERE chat_id = $1;'
        res = self.connection.fetchrow(query, (chat_id,))
        return SubscriberDTO(res[0], res[1])


class PostgresUserRepo(BaseUserRepo):
    async def add_user(self, user: UserDTO):
        query = 'INSERT INTO USERS VALUES ($1, $2, $3);'
        await self.connection.execute(
            query, (user.chat_id, user.username, user.full_name)
        )

    async def get_all_users(self) -> list[UserDTO]:
        query = 'SELECT chat_id, username, full_name from users;'
        res = await self.connection.fetchmany(query)
        return [UserDTO(x[0], x[1], x[2]) for x in res]

    async def get_user(self, chat_id) -> UserDTO:
        query = 'SELECT chat_id, username, full_name from users where chat_id = $1;'
        res = await self.connection.fetchrow(query, (chat_id,))
        return UserDTO(res[0], res[1], res[2])
