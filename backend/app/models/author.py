import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Boolean, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

article_authors = Table(
    "article_authors", Base.metadata,
    Column("article_id", UUID(as_uuid=True), ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True),
    Column("author_id", UUID(as_uuid=True), ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True),
    Column("author_order", Integer, nullable=False, default=1),
    Column("is_corresponding", Boolean, default=False),
)

class Author(Base):
    __tablename__ = "authors"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(256), nullable=False, index=True)
    normalized_name = Column(String(256), nullable=True, index=True)
    affiliation = Column(Text, nullable=True)
    department = Column(Text, nullable=True)
    country = Column(String(128), nullable=True, index=True)
    country_code = Column(String(8), nullable=True)
    city = Column(String(128), nullable=True)
    email = Column(String(255), nullable=True)
    orcid = Column(String(32), nullable=True, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    articles = relationship("Article", secondary=article_authors, back_populates="authors")
