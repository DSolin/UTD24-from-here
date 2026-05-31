import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Date, DateTime, Integer, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

article_keywords = Table(
    "article_keywords", Base.metadata,
    Column("article_id", UUID(as_uuid=True), ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True),
    Column("keyword_id", UUID(as_uuid=True), ForeignKey("keywords.id", ondelete="CASCADE"), primary_key=True),
)

class Article(Base):
    __tablename__ = "articles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(Text, nullable=False)
    abstract = Column(Text, nullable=True)
    doi = Column(String(512), unique=True, nullable=True, index=True)
    published_date = Column(Date, nullable=True, index=True)
    published_online_date = Column(Date, nullable=True)
    volume = Column(String(32), nullable=True)
    issue = Column(String(32), nullable=True)
    pages = Column(String(64), nullable=True)
    article_type = Column(String(64), nullable=True, default="research_article")
    pdf_url = Column(Text, nullable=True)
    source_url = Column(Text, nullable=True)
    source_platform = Column(String(64), nullable=True)
    language = Column(String(16), nullable=True, default="en")
    citation_count = Column(Integer, nullable=True, default=0)
    crawled_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    journal_id = Column(UUID(as_uuid=True), ForeignKey("journals.id", ondelete="CASCADE"), nullable=False, index=True)
    journal = relationship("Journal", back_populates="articles")
    authors = relationship("Author", secondary="article_authors", back_populates="articles")
    keywords = relationship("Keyword", secondary=article_keywords, back_populates="articles")
    favorited_by = relationship("Favorite", back_populates="article", cascade="all, delete-orphan")
