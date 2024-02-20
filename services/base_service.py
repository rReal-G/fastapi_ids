
from typing import Annotated

from fastapi import Depends
from models.artist import Artist
from models.song import Song
from repository.base_repository import ArtistRepository, _BaseG_Compatible, BaseRepository
from schemas.artist import ArtistSchema_Create, ArtistSchema_Read, ArtistSchema_Update


class CrudServiceBase:
    
    _repo:BaseRepository

    def get_all(self, orm_class:type[_BaseG_Compatible]):
        return self._repo.read_all(orm_class)       
    def get_by_id(self, id:int, orm_class:type[_BaseG_Compatible]):
        return self._repo.read_by_id(id, orm_class)
    def create(self, input_data):
        raise NotImplementedError('do not instantiate this class')
    def update(self, id, updates):
        raise NotImplementedError('do not instantiate this class')
    def delete(self, id:int, orm_class:type[_BaseG_Compatible]):
        to_be_erased = self.get_by_id(id, orm_class)
        return self._repo.delete(to_be_erased)
    
    
    

        