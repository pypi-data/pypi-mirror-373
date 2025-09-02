from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ZoteroTask(BaseModel):
    title: str
    author: str
    ms_of_bookmark_timestamp: int
    ms_of_bookmark_chapter: int
    timestamp: datetime


class AudiobookFinished(BaseModel):
    title: str


class DefaultModel(BaseModel):
    start: datetime
    end: datetime


class Exercise(DefaultModel):
    type: str


class MeditationSession(Exercise):
    pass


class YogaSession(Exercise):
    pass


class ReadingSession(DefaultModel):
    title: str
    page_old: int
    page_new: int
    reading_type: str
    finished: Optional[bool] = False


class NewBook(BaseModel):
    title: str
    type: str


class Timer(DefaultModel):
    context: str


class AppUsage(DefaultModel):
    app: str


class Power(BaseModel):
    type: str


class DrugSession(BaseModel):
    beer: Optional[str]
    wine: Optional[str]
    liquor: Optional[str]
    other: Optional[str]
    water: Optional[str]
