from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal
from models import User, Post, Tag
from enums import Level, Category, Tags as TagsEnum
from datetime import datetime

# Recreate the database (for testing purposes)
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

def test_tags():
    db: Session = SessionLocal()
    
    try:
        # 1. Create a user
        user = User(username="testuser", email="test@example.com")
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # 2. Create tags
        tag1 = Tag(name="Python")
        tag2 = Tag(name="FastAPI")
        db.add_all([tag1, tag2])
        db.commit()
        db.refresh(tag1)
        db.refresh(tag2)
        
        # 3. Create a post with tags
        post = Post(
            title="Learning FastAPI",
            content="FastAPI is great for building APIs.",
            author=user,
            level=Level.BEGINNER.value,
            category=Category.FASTAPI.value,
            tags=[tag1, tag2]
        )
        db.add(post)
        db.commit()
        db.refresh(post)
        
        print(f"Created Post ID: {post.id}")
        print(f"Post Tags: {[tag.name for tag in post.tags]}")
        
        # 4. Verify Many-to-Many
        # Check if tag1 has the post
        print(f"Tag '{tag1.name}' associated posts: {[p.title for p in tag1.posts]}")
        
        assert len(post.tags) == 2
        assert "Python" in [t.name for t in post.tags]
        assert "FastAPI" in [t.name for t in post.tags]
        assert len(tag1.posts) == 1
        
        print("\nVerification Successful!")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_tags()
