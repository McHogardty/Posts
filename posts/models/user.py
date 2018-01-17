"""Define the models for users and their associated posts."""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


class User(Base):
    """Represent a user. Users have the following properties:

    - Name: The user's name.
    - Email: The user's email address.
    - Posts: A user has many posts.

    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)

    posts = relationship("Post", back_populates="user")

    def to_dict(self):
        """Create a dictionary representation of the User instance."""

        return {"id": self.id, "name": self.name, "email": self.email}


class Post(Base):
    """Represent a post. Posts have the following properties:

    - Title: A title of the post.
    - Body: The full content of the post.

    """

    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    body = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", back_populates="posts")

    def to_dict(self):
        return {"id": self.id, "title": self.title, "body": self.body}
