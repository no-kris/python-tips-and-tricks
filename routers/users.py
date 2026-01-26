from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from crud.users import get_user_by_email, get_user_by_id, get_user_by_username
from database import get_db
from schemas import PostResponse, UserCreate, UserResponse, UserUpdate

router = APIRouter()


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    # Check if username already exists
    existing_user = await get_user_by_username(user.username, db)
    if existing_user:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Username already exists."
        )
    # Check if email already exists
    existing_email = await get_user_by_email(user.email, db)
    if existing_email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Email already exists.")
    # Create user
    new_user = models.User(username=user.username, email=user.email)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    user = await get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Could not find user.")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    user = await get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    await db.delete(user)
    await db.commit()


@router.patch("/{user_id}")
async def update_user(
    user_id: int, user_update: UserUpdate, db: Annotated[AsyncSession, Depends(get_db)]
):
    user = await get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found.")
    # Check if username is not empty and it's not already taken,
    if user_update.username is not None and user_update.username != user.username:
        existing_user = await get_user_by_username(user_update.username, db)
        if existing_user:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, detail="Username already taken."
            )
    # Check if email is not empty and that it's not already in use.
    if user_update.email is not None and user_update.email != user.email:
        existing_email = await get_user_by_email(user_update.email, db)
        if existing_email:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, detail="Email is already in use."
            )
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/{user_id}/posts", response_model=list[PostResponse])
async def get_user_posts(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    user = await get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found.")
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author), selectinload(models.Post.tags))
        .where(models.Post.user_id == user_id)
    )
    posts = result.scalars().all()
    return posts
