import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class BaseG(Base):
    __abstract__ = True
    id:Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    created_at:Mapped[datetime.date] = mapped_column(default=datetime.date.today)
