from pydantic import BaseModel, ConfigDict, Field
from enums import Level, Category, Tags

class PostBase(BaseModel):
    """Base post model. Shared between creating and returning post data."""

    title: str = Field(min_length=2, max_length=100)
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
    created_at: str
    published: bool
    level: Level
    category: Category
    tags: list[Tags]