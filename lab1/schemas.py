# app/schemas.py
from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class LabelCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)

    @field_validator("name")
    @classmethod
    def normalize(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("must not be empty")
        return v.lower()   # store normalized

class LabelOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}

class TodoBase(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    due_date: Optional[datetime] = None
    labels: Optional[List[str]] = None   # label names (normalized)

    @field_validator("labels")
    @classmethod
    def normalize_labels(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is None:
            return v
        cleaned = []
        seen = set()
        for name in v:
            name = name.strip().lower()
            if not name:
                raise ValueError("label names must not be empty")
            if name in seen:
                raise ValueError("label should be unique")
            
            cleaned.append(name)
            
        return cleaned

class TodoCreate(TodoBase):
    title: str = Field(min_length=1, max_length=200)
    labels: Optional[List[str]] = []

class TodoUpdate(TodoBase):
    # All fields optional; if `labels` provided, it replaces the set
    # If you also want to allow toggling `done` here:
    done: Optional[bool] = None

class TodoOut(BaseModel):
    id: int
    title: str
    done: bool
    due_date: Optional[datetime]
    labels: List[str]  # expose names (not objects)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
