from typing import Any, TypeVar
from requests import session
from sqlalchemy import create_engine
from fastapi import HTTPException

from sqlalchemy import Select
from sqlalchemy.orm.session import Session, sessionmaker
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import Protocol
from models.song import Song
from models.artist import Artist
from models.base import Base, BaseG
from schemas.artist import ArtistSchema_Create, ArtistSchema_Update

SQLALCHEMY_DATABASE_URL = "sqlite:///database.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
session_maker = sessionmaker(bind=engine)

def get_db():
    with session_maker() as ss:
        yield ss

# class HasId(Protocol):
#     id: int

# T = TypeVar('T', bound=HasId)

BaseG_Compatible = TypeVar('BaseG_Compatible', bound=BaseG)

def read_all(db:Session, orm_class:type[BaseG_Compatible]) -> list[BaseG_Compatible]:
    return db.query(orm_class).all()

def create(db: Session, instance:BaseG_Compatible) -> BaseG_Compatible:
    db.add(instance)
    db.commit()
    return instance

def read_by_id(db: Session, instance_id:int, orm_class: type[BaseG_Compatible]) -> BaseG_Compatible | None:
    if not hasattr(orm_class, 'id'):
        raise ValueError("Instance must have an 'id' attribute")
    return db.query(orm_class).filter(orm_class.id == instance_id).first()

def delete(db: Session, instance):
    db.delete(instance)
    db.commit()
    return instance

# def update_remove_child(db:Session, parent:Artist, child:Song):
#     parent.songs.remove(child)
#     db.commit()

def update(db: Session, instance: BaseG_Compatible, 
           updates: ArtistSchema_Update) -> BaseG_Compatible:
    for attr, value_input in updates.dict().items():
        instance_attr_val = getattr(instance, attr)
        if type(value_input) is not type(instance_attr_val) and \
            not (isinstance(value_input, list) and isinstance(instance_attr_val, list)):
            raise HTTPException(status_code=400, detail='wrong field type')
        elif isinstance(instance_attr_val, (list,set)):
            instance_attr_val:list
            new_item = [i for i in value_input if not i['id']]
            old_only_value_input = [v for v in value_input if v not in new_item]
            old_item_db = [i for i in instance_attr_val 
                        if getattr(i, 'id') in [j['id'] for j in value_input]]
            # if len(old_item_db) != len(instance_attr_val) - len(new_item):
            #     raise HTTPException(status_code=400, detail='non existent child item id(s)')
            # l:list[Any] = list(new_item)
            for item_db in old_item_db:
                for item_input in old_only_value_input:
                    if item_db.id == item_input['id']:
                        dicc = item_input.items()
                        for k,v in dicc:
                            setattr(item_db, k, v)
            instance_attr_val.extend(new_item)
        elif hasattr(instance, attr):            
            setattr(instance, attr, value_input)
    db.commit()
    db.refresh(instance)
    return instance

# from contextlib import contextmanager
# @contextmanager
# def get_file():
#     with open('test.py', 'r') as file:
#         yield file
#         # contents = file.read()
#         # return contents   

# from contextlib import contextmanager
# @contextmanager
# def get_file2():
#     try:
#         file = open('test.py', 'r')
#         yield file
#         # with open('test.py', 'r') as file:
#         #     yield file
#     finally:
#         file.close()
#         #yield file


# with get_file() as file:
#     print(file.readline())
# print(file.closed)
# #print(file.readline())
        
# # f = get_file2()
# # file = next(f)
# # print(file.readline())
# # next(f)
# # print(file.readline())