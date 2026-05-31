"""关键词"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.article import article_keywords

class Keyword(Base):
    __tablename__ = "keywords"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    keyword = Column(String(256), nullable=False, index=True)
    normalized_keyword = Column(String(256), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    articles = relationship("Article", secondary=article_keywords, back_populates="keywords")
