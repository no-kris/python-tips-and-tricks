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
