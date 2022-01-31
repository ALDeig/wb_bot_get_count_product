from datetime import date, timedelta

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, DBAPIError

from tgbot.models.tables import User, Tracking


async def add_new_tracking(session: AsyncSession, product_id: int, count: int, user_id: int):
    """Добавляет новое отслеживание"""
    tracking = Tracking(user_id=user_id, product_id=product_id, count=count)
    session.add(tracking)
    try:
        await session.commit()
        return True
    except DBAPIError:
        await session.rollback()


async def add_user(session: AsyncSession, user_id: int, subscribe: int) -> bool:
    """
    Добавляет нового пользователя
    :param session:
    :param user_id:
    :param subscribe: Количество дней, на сколько активируется подписка у человека
    :return:
    """
    user = User(id=user_id, subscribe=date.today() + timedelta(days=subscribe))
    session.add(user)
    try:
        await session.commit()
        return True
    except (IntegrityError, DBAPIError):
        await session.rollback()
        return False


async def get_user(session: AsyncSession, user_id: int) -> User | None:
    """Возвращает объект пользователя если он есть в базе, иначе None"""
    user = await session.execute(sa.select(User).where(User.id == user_id))
    return user.scalar()


async def delete_user(session: AsyncSession, user_id: int):
    """Удаляет пользователя по его id"""
    result = await session.execute(sa.delete(User).where(User.id == user_id).returning("*"))
    await session.commit()
    if result.fitst():
        return True
    return


async def get_users(session: AsyncSession) -> list[User]:
    users = await session.execute(sa.select(User).order_by(User.id))
    return users.scalars().all()


async def remove_users_without_subscribe(session: AsyncSession):
    """Удаляет пользователей у которых срок подписки меньше сегодняшней даты"""
    await session.execute(sa.delete(User).where(User.subscribe < date.today()))
    await session.commit()


async def get_all_tracking(session: AsyncSession) -> list[Tracking]:
    """Возвращает все отслеживания в базе"""
    tracking = await session.execute(sa.select(Tracking).order_by(Tracking.user_id))
    return tracking.scalars().all()


if __name__ == '__main__':
    import asyncio
    from tgbot.services.db_connection import get_session


    async def main():
        session = await get_session()
        requests = await add_user(session, 12234, 3)
        print(requests)
        await session.close()

    asyncio.run(main())
