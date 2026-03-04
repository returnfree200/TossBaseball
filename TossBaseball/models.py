from sqlalchemy import Column, BigInteger, Text, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(Text, nullable=False, unique=True)
    name = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # 관계 설정: 한 유저는 여러 메모를 가질 수 있음 (1:N)
    memos = relationship("Memo", back_populates="author", cascade="all, delete")

class Memo(Base):
    __tablename__ = "memos"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # 관계 설정: 메모는 한 명의 작성자에게 속함
    author = relationship("User", back_populates="memos")

# 인덱스 설정 (요구사항 반영)
# 1. 특정 유저의 메모를 최신순으로 조회할 때 사용
Index("idx_memos_user_created_at", Memo.user_id, Memo.created_at.desc())
# 2. 모든 메모를 최신순으로 조회할 때 사용
Index("idx_memos_created_at", Memo.created_at.desc())