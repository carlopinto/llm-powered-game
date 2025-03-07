from __future__ import annotations
from typing import List

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from llmgame.database import db

class User(db.Model):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    started = Column(DateTime(timezone=True), server_default=func.now())
    lifeline_5050 = Column(Boolean, server_default='0')
    lifeline_flip = Column(Boolean, server_default='0')
    lifeline_host = Column(Boolean, server_default='0')
    lifeline_audiance = Column(Boolean, server_default='0')
    questions: Mapped[List["Question"]] = relationship()
    

class Question(db.Model):
    __tablename__ = "question"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    index: Mapped[int] = mapped_column(nullable=False)
    topic: Mapped[str] = mapped_column(nullable=False)
    surprise_topic = Column(Boolean, server_default='0')
    question: Mapped[str] = mapped_column(nullable=False)
    answer: Mapped[str] = mapped_column(nullable=False)
    option_a: Mapped[str] = mapped_column(nullable=False)
    option_b: Mapped[str] = mapped_column(nullable=False)
    option_c: Mapped[str] = mapped_column(nullable=False)
    option_d: Mapped[str] = mapped_column(nullable=False)
    user_answer: Mapped[str] = mapped_column(nullable=True)
