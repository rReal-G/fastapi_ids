from typing import TypeVar
from sqlalchemy import create_engine

from sqlalchemy.orm.session import Session, sessionmaker
from sqlalchemy.orm import selectinload

import utils.decorators as deco
from models.song import Song
from models.artist import Artist
from schemas.artist import ArtistSchema_Update
from repository.baseG_type import _BaseG_Compatible





class BaseRepository:
    SQLALCHEMY_DATABASE_URL = "sqlite:///database.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
    session_maker = sessionmaker(bind=engine, autoflush=False)

    @staticmethod
    def get_db():
        with  BaseRepository.session_maker() as ss:
            yield ss
    
    @staticmethod
    def session_wrapped_decorator(repo_func):
        def wrapped(*args, **kwagrs):
            if 'db' not in kwagrs.keys() or kwagrs['db']:
                with  BaseRepository.session_maker() as ss:
                    return repo_func(*args, **kwagrs, db=ss)
            else:
                return repo_func(*args, *kwagrs)
        return wrapped

    _relationship = []
    
    @session_wrapped_decorator
    def read_all(self, orm_class:type[_BaseG_Compatible], *, db:Session|None=None) -> list[_BaseG_Compatible]:
        assert db is not None
        query = db.query(orm_class)
        for relala in self._relationship:
            query = query.options(selectinload(relala))
        return query.all()
    
    @deco.Utils_Decorators.toggle_raise_for_not_found(on=True, detail='resource not found')
    @session_wrapped_decorator
    def read_by_id(self, instance_id:int, 
                   orm_class: type[_BaseG_Compatible], 
                   *, db:Session|None=None
                   ) -> _BaseG_Compatible | None:
        if not hasattr(orm_class, 'id'):
            raise ValueError("Instance must have an 'id' attribute")
        assert db is not None
        query =  db.query(orm_class).filter(orm_class.id == instance_id)
        for relala in self._relationship:
            query = query.options(selectinload(relala))
        return query.first()
    
    @session_wrapped_decorator
    def delete(self, instance, *, db: Session|None=None):
        assert db is not None
        db.delete(instance)
        db.commit()
        return instance
    
class ArtistRepository(BaseRepository):
    _relationship = [Artist.songs]
    
    @BaseRepository.session_wrapped_decorator
    def create(self, instance:_BaseG_Compatible, *, db: Session|None=None):
        assert db is not None
        db.add(instance)
        db.commit()
        #db.refresh(instance) #no eagerload for refresh, go requerying
        return instance.id

    # def update_remove_child(db:Session, parent:Artist, child:Song):
    #     parent.songs.remove(child)
    #     db.commit()

    @BaseRepository.session_wrapped_decorator
    @deco.Utils_Decorators.update_wrap
    def update(self, *, db:Session|None=None, 
                      instance:_BaseG_Compatible,  
                      updates:ArtistSchema_Update
                      ):  
        d = updates.model_dump(exclude_unset=True, exclude_defaults=True, exclude={'songs'})
        #l = [(attr, val) for attr, val in updates.model_dump().items() if isinstance(val, list)]
        songs_pydantic = updates.songs
        songs_orm = [Song(**s_dict.model_dump(exclude_unset=True)) for s_dict in songs_pydantic]
        new_artist = Artist(**d, id=instance.id)
        new_artist.songs.extend(songs_orm)
        return new_artist


        





