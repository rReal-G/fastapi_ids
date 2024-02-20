from enum import unique
from typing import TYPE_CHECKING
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql.sqltypes import Boolean, DateTime, Float
import datetime
from models.base import Base, BaseG
import models.song
from sqlalchemy.ext.mutable import MutableList

class Artist(BaseG):
    __tablename__ = 'Artist_table'
    #id:Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    # created_at:Mapped[datetime.date] = mapped_column(default=datetime.date.today)
    name:Mapped[str] = mapped_column(String(200))
    age:Mapped[int] = mapped_column()

    songs:Mapped[list['models.song.Song']] = relationship(
        back_populates='artist', 
        cascade='all, delete, delete-orphan',
        )
    

