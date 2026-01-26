from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models


async def get_user_by_id(user_id: int, db: AsyncSession):
    """
    Return first instance of a user from the database matching the user id.
    Else None.
    """
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    return result.scalars().first()


async def get_user_by_username(username: str, db: AsyncSession):
    """
    Return first instance of user from database matching the users username.
    Else None.
    """
    result = await db.execute(
        select(models.User).where(models.User.username == username),
    )
    return result.scalars().first()


async def get_user_by_email(email: str, db: AsyncSession):
    """
    Return first instance of user from database matching the users email.
    Else None.
    """
    result = await db.execute(
        select(models.User).where(models.User.email == email),
    )
    return result.scalars().first()
