from enum import unique
from typing import TYPE_CHECKING
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql.sqltypes import Boolean, DateTime, Float
import datetime
from models.playlist_song import Playlist_Song
import models.song
from models.base import Base, BaseG
from sqlalchemy.ext.mutable import MutableList

class Playlist(BaseG):
    __tablename__ = 'Playlist_table'
    # id:Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    # created_at:Mapped[datetime.date] = mapped_column(default=datetime.date.today)
    name:Mapped[str] = mapped_column(String(200))

    songs:Mapped[list['models.song.Song']] = relationship(
        secondary=Playlist_Song,
        back_populates='related_playlists'
    )

