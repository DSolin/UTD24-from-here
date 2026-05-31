"""期刊"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class Journal(Base):
    __tablename__ = "journals"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(512), unique=True, nullable=False, index=True)
    abbreviation = Column(String(128), nullable=True)
    publisher = Column(String(256), nullable=True)
    issn = Column(String(32), nullable=True, unique=True)
    eissn = Column(String(32), nullable=True)
    url = Column(Text, nullable=True)
    platform = Column(String(64), nullable=True)
    utd24_index = Column(Integer, nullable=True)
    cover_image_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    articles = relationship("Article", back_populates="journal", cascade="all, delete-orphan")
    crawl_logs = relationship("CrawlLog", back_populates="journal", cascade="all, delete-orphan")
