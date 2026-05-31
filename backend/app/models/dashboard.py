"""仪表板布局 & 爬取日志"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base

class UserDashboardLayout(Base):
    __tablename__ = "user_dashboard_layouts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(128), nullable=False, default="Default Layout")
    layout_config = Column(JSONB, nullable=False, default=dict)
    is_default = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    user = relationship("User", back_populates="dashboard_layouts")

class CrawlLog(Base):
    __tablename__ = "crawl_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    journal_id = Column(UUID(as_uuid=True), ForeignKey("journals.id", ondelete="SET NULL"), nullable=True, index=True)
    status = Column(String(32), nullable=False, default="pending")
    articles_found = Column(Integer, default=0)
    articles_new = Column(Integer, default=0)
    articles_skipped = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    journal = relationship("Journal", back_populates="crawl_logs")
