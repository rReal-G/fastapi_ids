from enum import unique
from typing import TYPE_CHECKING
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql.sqltypes import Boolean, DateTime, Float
import datetime
import models.playlist
import models.artist
from models.base import Base, BaseG
from sqlalchemy.ext.mutable import MutableList

from models.playlist_song import Playlist_Song

class Song(BaseG):
    __tablename__ = 'Song_table'
    # id:Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    # created_at:Mapped[datetime.date] = mapped_column(default=datetime.date.today)
    name:Mapped[str] = mapped_column(String(200))

    artist_id:Mapped[int] = mapped_column(ForeignKey(column='Artist_table.id'))
    artist:Mapped['models.artist.Artist'] = relationship(back_populates='songs')

    related_playlists:Mapped[list['models.playlist.Playlist']] = relationship(
        secondary=Playlist_Song,
        back_populates='songs'
    )
