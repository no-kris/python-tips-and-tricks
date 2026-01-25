from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.exceptions import HTTPException as StarletteHTTPException

import models
from database import AsyncSessionLocal, Base, engine, get_db
from schemas import (
    PostCreate,
    PostResponse,
    PostUpdate,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from utils import format_date, get_db_tags, seed_tags


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        await seed_tags(db)

    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
templates.env.filters["format_date"] = format_date


@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
async def home(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.Post).options(
            selectinload(models.Post.author), selectinload(models.Post.tags)
        )
    )
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request, "home.html", {"posts": posts, "title": "Home"}
    )


@app.get("/posts/{user_id}/post", include_in_schema=False, name="user_posts_page")
async def user_posts_page(
    request: Request, user_id: int, db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found.")
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author), selectinload(models.Post.tags))
        .where(models.Post.user_id == user_id)
    )
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {"posts": posts, "user": user, "title": f"{user.username}'s Posts"},
    )


@app.get("/posts/{post_id}", include_in_schema=False)
async def post_page(
    request: Request, post_id: int, db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author), selectinload(models.Post.tags))
        .where(models.Post.id == post_id)
    )
    post = result.scalars().first()
    if post:
        title = post.title[:20]
        return templates.TemplateResponse(
            request, "post.html", {"post": post, "title": title}
        )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")


@app.get("/api/user/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Could not find user.")
    return user


@app.get("/api/user/{user_id}/posts", response_model=list[PostResponse])
async def get_user_posts(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found.")
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author), selectinload(models.Post.tags))
        .where(models.Post.user_id == user_id)
    )
    posts = result.scalars().all()
    return posts


@app.patch("/api/user/{user_id}")
async def update_user(
    user_id: int, user_update: UserUpdate, db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found.")
    # Check if username is not empty and it's not already taken,
    if user_update.username is not None and user_update.username != user.username:
        result = await db.execute(
            select(models.User).where(models.User.username == user_update.username)
        )
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, detail="Username already taken."
            )
    # Check if email is not empty and that it's not already in use.
    if user_update.email is not None and user_update.email != user.email:
        result = await db.execute(
            select(models.User).where(models.User.email == user_update.email)
        )
        existing_email = result.scalars().first()
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


@app.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    await db.delete(user)
    await db.commit()


@app.get("/api/posts/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author), selectinload(models.Post.tags))
        .where(models.Post.id == post_id)
    )
    post = result.scalars().first()
    if post:
        return post
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Post not found.")


@app.put("/api/posts/{post_id}")
async def update_post_full(
    post_id: int, post_data: PostCreate, db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author), selectinload(models.Post.tags))
        .where(models.Post.id == post_id)
    )
    post = result.scalars().first()
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Post not found.")
    # Make sure it's the correct user updating the post.
    if post_data.user_id != post.user_id:
        result = await db.execute(
            select(models.User).where(models.User.id == post_data.user_id)
        )
        user = result.scalars().first()
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found.")
    post.title = post_data.title
    post.content = post_data.content
    post.user_id = post_data.user_id
    post.level = post_data.level.value
    post.category = post_data.category.value
    post.tags = await get_db_tags(db, post_data.tags)
    await db.commit()
    await db.refresh(post, attribute_names=["author", "tags"])
    return post


@app.patch("/api/posts/{post_id}")
async def update_post_partial(
    post_id: int, post_data: PostUpdate, db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author), selectinload(models.Post.tags))
        .where(models.Post.id == post_id)
    )
    post = result.scalars().first()
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Post not found.")
    update_data = post_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)
    await db.commit()
    await db.refresh(post, attribute_names=["author", "tags"])
    return post


@app.delete("/api/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author), selectinload(models.Post.tags))
        .where(models.Post.id == post_id)
    )
    post = result.scalars().first()
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Post not found.")
    await db.delete(post)
    await db.commit()


@app.post(
    "/api/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    # Check if username already exists
    result = await db.execute(
        select(models.User).where(models.User.username == user.username),
    )
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Username already exists."
        )
    # Check if email already exists
    result = await db.execute(
        select(models.User).where(models.User.email == user.email),
    )
    existing_email = result.scalars().first()
    if existing_email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Email already exists.")
    # Create user
    new_user = models.User(username=user.username, email=user.email)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@app.post(
    "/api/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(post: PostCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == post.user_id))
    user = result.scalars().first()
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


@app.get("/api/posts", response_model=list[PostResponse])
async def get_posts(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.Post).options(
            selectinload(models.Post.author), selectinload(models.Post.tags)
        )
    )
    posts = result.scalars().all()
    return posts


@app.exception_handler(StarletteHTTPException)
async def general_http_exception_handler(
    request: Request, exception: StarletteHTTPException
):
    if request.url.path.startswith("/api"):
        return await http_exception_handler(request, exception)

    message = (
        exception.detail if exception.detail else "Got an error. Please try again."
    )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code,
    )


@app.exception_handler(RequestValidationError)
async def validaton_exception_handler(
    request: Request, exception: RequestValidationError
):
    if request.url.path.startswith("/api"):
        return await request_validation_exception_handler(request, exception)

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Bad request. Please try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )
