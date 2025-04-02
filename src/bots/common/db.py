from abc import ABC, abstractmethod

from bots.common.models import SubscriberDTO, UserDTO


class BaseSubscriberRepo(ABC):
    def __init__(self, conn):
        self.connection = conn

    @abstractmethod
    async def get_all_subscribers(self) -> list[SubscriberDTO]:
        pass

    @abstractmethod
    async def get_all_channel_subscribers(
        self, channel_id: int
    ) -> list[SubscriberDTO]:
        pass

    @abstractmethod
    async def add_subscriber(self, subscriber: SubscriberDTO):
        pass

    @abstractmethod
    async def remove_subscriber(self, subscriber_id: int) -> None:
        pass

    @abstractmethod
    async def get_subscriber(self, user_id) -> SubscriberDTO | None:
        pass

    @abstractmethod
    async def check_subscriber_exists(self, user_id) -> bool:
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
    async def get_user(self, user_id: int) -> UserDTO | None:
        pass

    @abstractmethod
    async def check_user_exists(self, user_id: int) -> bool:
        pass


class PostgresSubscriberRepo(BaseSubscriberRepo):
    async def get_all_subscribers(self) -> list[SubscriberDTO]:
        query = 'SELECT user_id, channel_id from subscribers;'
        res = await self.connection.fetch(query)
        return [SubscriberDTO(user_id=x[0], channel_id=x[1]) for x in res]

    async def get_all_channel_subscribers(
        self, channel_id
    ) -> list[SubscriberDTO]:
        query = 'SELECT user_id, channel_id FROM subscribers WHERE channel_id = $1;'
        res = await self.connection.fetch(query, channel_id)
        print(res)
        return [SubscriberDTO(user_id=x[0], channel_id=x[1]) for x in res]

    async def add_subscriber(self, subscriber: SubscriberDTO):
        query = 'INSERT INTO subscribers VALUES ($1, $2);'
        await self.connection.execute(
            query, subscriber.user_id, subscriber.channel_id
        )

    async def remove_subscriber(self, subscriber_id):
        query = 'DELETE FROM subscribers WHERE user_id = $1;'
        await self.connection.fetchrow(query, subscriber_id)

    async def get_subscriber(self, user_id) -> SubscriberDTO | None:
        query = (
            'SELECT user_id, channel_id FROM subscribers WHERE user_id = $1;'
        )
        res = await self.connection.fetchrow(query, user_id)
        if res:
            return SubscriberDTO(user_id=res[0], channel_id=res[1])
        else:
            return None

    async def check_subscriber_exists(self, user_id):
        subscriber = await self.get_subscriber(user_id)
        return bool(subscriber)


class PostgresUserRepo(BaseUserRepo):
    async def add_user(self, user: UserDTO):
        query = 'INSERT INTO users VALUES ($1, $2, $3) ON CONFLICT DO NOTHING;'

        await self.connection.execute(
            query,
            user.chat_id,
            user.username,
            user.full_user_name,
        )

    async def get_all_users(self) -> list[UserDTO]:
        query = 'SELECT chat_id, username, full_name from users;'
        res = await self.connection.fetch(query)
        return [
            UserDTO(chat_id=x[0], username=x[1], full_user_name=x[2])
            for x in res
        ]

    async def get_user(self, user_id) -> UserDTO | None:
        query = 'SELECT chat_id, username, full_user_name from users where chat_id = $1;'
        res = await self.connection.fetchrow(query, user_id)
        print(res)
        if res:
            return UserDTO(
                chat_id=res[0], username=res[1], full_user_name=res[2]
            )
        return None

    async def check_user_exists(self, user_id):
        subscriber = await self.get_user(user_id)
        return bool(subscriber)
