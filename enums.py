from enum import Enum

class Level(str, Enum):
    """Defines the experience level given to a post."""

    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


class Category(str, Enum):
    """Defines a category given to a post."""

    BASICS = "Python Basics"
    FASTAPI = "FastAPI"
    FLASK = "Flask"
    DJANGO = "Django"
    DATA_SCIENCE = "Data Science"
    WEB_DEV = "Web Dev"

class Tags(str, Enum):
    """Defines a tags a post can have. Each post can have multiple tags."""

    TUTORIAL = "Tutorial"
    TIPS = "Tips"
    ASYNC = "Asynchronous"
    DATA_STRUCTURES = "Data Structures"
    PERFORMANCE = "Performance"