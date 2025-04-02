from aiogram import BaseMiddleware

from bots.common.db import PostgresSubscriberRepo, PostgresUserRepo


class DbMiddleware(BaseMiddleware):
    skip_patterns = ['error', 'update']

    def __init__(self, pool):
        super().__init__()
        self.pool = pool

    async def __call__(self, handler, event, data):
        db = await self.pool.acquire()

        user_repo = PostgresUserRepo(db)
        subscriber_repo = PostgresSubscriberRepo(db)
        data['connection'] = db
        data['user_repo'] = user_repo
        data['subscriber_repo'] = subscriber_repo

        await handler(event, data)

        del data['user_repo']
        del data['subscriber_repo']
        db = data.get('connection')
        if db:
            await self.pool.release(db)
