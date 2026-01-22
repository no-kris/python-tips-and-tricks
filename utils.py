from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

import models
from enums import Tags


def format_date(date_str: str, fmt: str = "%B %d, %Y (%A)"):
    """
    Parses an ISO format date string and returns it formatted.
    """
    dt = datetime.fromisoformat(date_str)
    return dt.strftime(fmt)


def seed_tags(db: Session):
    """Populate the db with the predefined tags in enums.py"""
    for tag in Tags:
        tag_name = tag.value
        result = db.execute(select(models.Tag).where(models.Tag.name == tag_name))
        if not result.scalars().first():
            db.add(models.Tag(name=tag_name))
    db.commit()


def get_db_tags(db: Session, tag_enums: list[Tags]) -> list[models.Tag]:
    """Fetches models.Tag instances from the database based on a list of Tags enums."""
    db_tags = []
    for tag_enum in tag_enums:
        tag_name = tag_enum.value
        tag_result = db.execute(select(models.Tag).where(models.Tag.name == tag_name))
        db_tag = tag_result.scalars().first()
        if db_tag:
            db_tags.append(db_tag)
    return db_tags
