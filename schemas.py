from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from enums import Category, Level, Tags


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


class UserUpdate(BaseModel):
    """Update (optional) fields for user data."""

    username: str | None = Field(default=None, min_length=2, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=120)


class PostBase(BaseModel):
    """Base post model. Shared between creating and returning post data."""

    title: str = Field(min_length=2, max_length=50)
    content: str = Field(min_length=2)


class PostCreate(PostBase):
    """Defines what data every created post can have. Inherits base data from PostBase."""

    level: Level
    category: Category
    tags: list[Tags]
    user_id: int  # Testing purpose


class PostUpdate(BaseModel):
    """Update (optional) fields for a post object."""

    title: str | None = Field(default=None, min_length=2, max_length=100)
    content: str | None = Field(default=None, min_length=2)
    level: Level | None
    category: Category | None = None
    tags: list[Tags] | None

    @field_validator("tags", mode="before")
    @classmethod
    def transform_tags_from_String(cls, value):
        if isinstance(value, list) and len(value) > 0:
            return [Tags(tag) for tag in value]
        return value


class PostResponse(PostBase):
    """Defines the post data returned by the api."""

    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    author: UserResponse
    created_at: datetime
    published: bool = True
    level: Level
    category: Category
    tags: list[Tags]

    @field_validator("tags", mode="before")
    @classmethod
    def transform_tags(cls, value):
        if (
            isinstance(value, list)
            and len(value) > 0
            and not isinstance(value[0], Tags)
        ):
            return [Tags(tag.name) for tag in value]
        return value
