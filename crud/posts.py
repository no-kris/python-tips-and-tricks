from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models


async def get_all_posts_from_db(db: AsyncSession):
    """
    Return all the posts in the databse. Retrn None if there are no posts.
    """
    result = await db.execute(
        select(models.Post).options(
            selectinload(models.Post.author), selectinload(models.Post.tags)
        )
    )
    return result.scalars().all()


async def get_post_by_id(post_id: int, db: AsyncSession):
    """
    Return first instance of post in database matching the post id.
    Else None.
    """
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author), selectinload(models.Post.tags))
        .where(models.Post.id == post_id)
    )
    return result.scalars().first()
