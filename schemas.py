from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, EmailStr
from enums import Level, Category, Tags


class UserBase(BaseModel):
    """Base model for user data."""

    username: str = Field(min_length=2, max_length=50)
    email: EmailStr = Field(max_length=120)

class UserCreate(UserBase):
    """Defines the data needed to create a new user."""
    pass

class UserResponse(UserBase):
    """Defines the response data returned for a user."""

    model_config = ConfigDict(from_attributes=True)
    id: int


class PostBase(BaseModel):
    """Base post model. Shared between creating and returning post data."""

    title: str = Field(min_length=2, max_length=50)
    content: str = Field(min_length=2)
    author: str = Field(min_length=2, max_length=50)


class PostCreate(PostBase):
    """Defines what data every created post can have. Inherits base data from PostBase."""

    level: Level
    category: Category
    tags: list[Tags]


class PostResponse(PostBase):
    """Defines the post data returned by the api."""

    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    published: bool = True
    level: Level
    category: Category
    tags: list[Tags]