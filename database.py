"""
데이터베이스 모델 정의
- 자동화 스케줄 관리
- 이메일 발송 이력 관리
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


class Schedule(Base):
    """자동화 스케줄 테이블"""
    __tablename__ = 'schedules'
    
    id = Column(Integer, primary_key=True)
    keyword = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    last_sent = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Schedule(id={self.id}, keyword='{self.keyword}', email='{self.email}')>"


class EmailHistory(Base):
    """이메일 발송 이력 테이블"""
    __tablename__ = 'email_history'
    
    id = Column(Integer, primary_key=True)
    schedule_id = Column(Integer, nullable=True)  # None이면 단발성 발송
    keyword = Column(String(200), nullable=False)
    recipient = Column(String(200), nullable=False)
    paper_count = Column(Integer, default=0)
    status = Column(String(50), nullable=False)  # 'success' or 'failed'
    error_message = Column(Text, nullable=True)
    email_content = Column(Text, nullable=True)
    sent_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<EmailHistory(id={self.id}, keyword='{self.keyword}', status='{self.status}')>"


# 데이터베이스 초기화
def init_db(db_path='sqlite:///paperdigest.db'):
    """데이터베이스 초기화"""
    engine = create_engine(db_path, echo=False)
    Base.metadata.create_all(engine)
    return engine


def get_session(engine):
    """세션 생성"""
    Session = sessionmaker(bind=engine)
    return Session()
