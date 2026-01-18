from __future__ import annotations
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

# Association table for many-to-many relationship between Posts and Tags
post_tag_association = Table(
    "post_tag_association",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class User(Base):
    """
    Represents a registered user that is signed up on the website.

    Attributes:
        id (int): Unique identifier for the user.
        username (str): Unique username (max 50 chars).
        email (str): Unique email address (max 120 chars).
        posts (list[Post]): Collection of blog posts authored by the user.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    posts: Mapped[list[Post]] = relationship(back_populates="author")


class Tag(Base):
    """
    Represents a tag that can be associated with multiple blog posts.

    Attributes:
        id (int): Unique identifier for the tag.
        name (str): Unique name of the tag (e.g., 'Python', 'Web Dev').
    """

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    posts: Mapped[list[Post]] = relationship(
        secondary=post_tag_association, back_populates="tags"
    )


class Post(Base):
    """
    Represents the data attributes for a single post.

    Attributes:
        id (int): Unique identifier for the post.
        title (string): Title of the post (max: 50 chars).
        content (text): Body content of the post (no char limit).
        user_id (int): Foreign key that references the author of the post.
        created_at (date): Timestamp for created post.
        level (str): Experience level for the post (max: 50 chars).
        category (str): Category of the post content (max: 50 chars).
        tags (list(str)): List of tags for the post (max: 50 chars per tag).
        author (User): Retrieves the user/author of the post.
    """

    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    level: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    tags: Mapped[list[Tag]] = relationship(
        secondary=post_tag_association, back_populates="posts"
    )
    author: Mapped[User] = relationship(back_populates="posts")