from enum import unique
from typing import TYPE_CHECKING
from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql.sqltypes import Boolean, DateTime, Float
import datetime
from models.base import Base
from sqlalchemy.ext.mutable import MutableList


Playlist_Song = Table(
    'Playlist_Song_table', 
    Base.metadata,  
    Column('playlist_id', Integer, ForeignKey('Playlist_table.id')),
    Column('song_id', Integer, ForeignKey('Song_table.id'))
)
