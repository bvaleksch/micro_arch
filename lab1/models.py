# app/models.py
from datetime import datetime
from typing import List
from sqlalchemy import (
    Integer, Boolean, DateTime, ForeignKey, String, Table, Column, func, Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

todo_labels = Table(
    "todo_labels",
    Base.metadata,
    Column("todo_id", ForeignKey("todos.id", ondelete="CASCADE"), primary_key=True),
    Column("label_id", ForeignKey("labels.id", ondelete="CASCADE"), primary_key=True),
)

class Label(Base):
    __tablename__ = "labels"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # store lowercase to enforce case-insensitive uniqueness at app level
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

class Todo(Base):
    __tablename__ = "todos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    done: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    labels: Mapped[List[Label]] = relationship(
        secondary=todo_labels, lazy="joined", order_by=Label.id
    )

