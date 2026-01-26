from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import models
from crud.posts import get_all_posts_from_db, get_post_by_id
from crud.users import get_user_by_id
from database import get_db
from schemas import PostCreate, PostResponse, PostUpdate
from utils import get_db_tags

router = APIRouter()


@router.post(
    "",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(post: PostCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    user = await get_user_by_id(post.user_id, db)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found.")

    new_post = models.Post(
        title=post.title,
        content=post.content,
        level=post.level.value,
        category=post.category.value,
        user_id=post.user_id,
        tags=await get_db_tags(db, post.tags),
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post, attribute_names=["author", "tags"])
    return new_post


@router.get("", response_model=list[PostResponse])
async def get_posts(db: Annotated[AsyncSession, Depends(get_db)]):
    posts = await get_all_posts_from_db(db)
    return posts


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    post = await get_post_by_id(post_id, db)
    if post:
        return post
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Post not found.")


@router.put(
    "/{post_id}",
    response_model=PostResponse,
)
async def update_post_full(
    post_id: int, post_data: PostCreate, db: Annotated[AsyncSession, Depends(get_db)]
):
    post = await get_post_by_id(post_id, db)
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Post not found.")
    # Prevent post categories from being changed.
    if post_data.category.value != post.category:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Cannot change the category of an existing post.",
        )
    # Make sure it's the correct user updating the post.
    if post_data.user_id != post.user_id:
        user = await get_user_by_id(post_data.user_id, db)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found.")
    post.title = post_data.title
    post.content = post_data.content
    post.user_id = post_data.user_id
    post.level = post_data.level.value
    post.tags = await get_db_tags(db, post_data.tags)
    await db.commit()
    await db.refresh(post, attribute_names=["author", "tags"])
    return post


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post_partial(
    post_id: int, post_data: PostUpdate, db: Annotated[AsyncSession, Depends(get_db)]
):
    post = await get_post_by_id(post_id, db)
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Post not found.")
    update_data = post_data.model_dump(exclude_unset=True)
    if "category" in update_data:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Cannot change the category of an existing post.",
        )
    if "tags" in update_data and update_data["tags"] is not None:
        post.tags = await get_db_tags(db, update_data.pop("tags"))
    for field, value in update_data.items():
        if field == "level" and value is not None:
            setattr(post, field, value.value)
        else:
            setattr(post, field, value)
    await db.commit()
    await db.refresh(post, attribute_names=["author", "tags"])
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    post = await get_post_by_id(post_id, db)
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Post not found.")
    await db.delete(post)
    await db.commit()
