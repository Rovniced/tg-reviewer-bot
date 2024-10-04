import os
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, create_engine, func, text
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.config import Config


class Base(AsyncAttrs, DeclarativeBase):
    pass


class ReviewerModel(Base):
    __tablename__ = "reviewers"  # 审核者数据
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, comment='用户id')
    approve_count: Mapped[int] = mapped_column(Integer, comment='通过稿件数量')
    reject_count: Mapped[int] = mapped_column(Integer, comment='拒绝稿件数量')
    approve_but_rejected_count: Mapped[int] = mapped_column(Integer, comment='通过但是最后被拒绝的稿件数量')
    reject_but_approved_count: Mapped[int] = mapped_column(Integer, comment='拒绝但是最后通过的稿件数量')
    last_time: Mapped[datetime] = mapped_column(
            DateTime(timezone=True), server_default=func.now(), comment='最后审核时间'
    )


class SubmitterModel(Base):
    __tablename__ = "submitters"  # 投稿者数据
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, comment='用户id')
    submission_count: Mapped[int] = mapped_column(Integer, comment='投稿数量')
    approved_count: Mapped[int] = mapped_column(Integer, comment='通过数量')
    rejected_count: Mapped[int] = mapped_column(Integer, comment='拒绝数量')


class BannedUserModel(Base):
    __tablename__ = "banned_users"
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, comment='用户id')
    user_name: Mapped[str] = mapped_column(String(50), nullable=True, comment='用户username')
    user_fullname: Mapped[str] = mapped_column(String(50), nullable=True, comment='用户姓名')
    banned_reason: Mapped[str] = mapped_column(String(50), nullable=True, comment='封禁原因')
    banned_date: Mapped[datetime] = mapped_column(
            DateTime(timezone=True), server_default=func.now(), comment='封禁日期'
    )
    banned_by: Mapped[int] = mapped_column(Integer, comment='封禁操作人ID')


def initialize_database(db_name, base):
    db_path = Config.DATABASES_DIR / db_name
    if not db_path.exists():
        os.makedirs(Config.DATABASES_DIR, exist_ok=True)
        sync_engine = create_engine(f"sqlite:///{db_path}")
        with sync_engine.begin() as connection:
            base.metadata.create_all(sync_engine)
            connection.execute(text('PRAGMA journal_mode = WAL'))  # 启用 WAL
    
    return create_async_engine(f'sqlite+aiosqlite:///{db_path}', echo=Config.SQLALCHEMY_LOG)


class ManuscriptBase(AsyncAttrs, DeclarativeBase):
    pass


class ManuscriptModel(ManuscriptBase):
    # 稿件数据
    __tablename__ = "manuscript"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True, comment='稿件id')
    approve: Mapped[str] = mapped_column(String, nullable=True, comment='投票通过的')
    reject: Mapped[str] = mapped_column(String, nullable=True, comment='投票拒绝的')
    submitter_id: Mapped[int] = mapped_column(Integer, comment='投稿者id')
    reject_reason: Mapped[str] = mapped_column(String, nullable=True, comment='拒绝原因')
    submitter_message_id: Mapped[int] = mapped_column(Integer, comment='投稿原始消息id')
    
    
# 统计数据库
statistic_engine = initialize_database('statistic.db', Base)
StatisticSessionFactory = async_sessionmaker(bind=statistic_engine, expire_on_commit=False)
# 稿件数据库
manuscript_engine = initialize_database('manuscript.db', ManuscriptBase)
ManuscriptSessionFactory = async_sessionmaker(bind=manuscript_engine, expire_on_commit=False)
