
from typing import Annotated

from fastapi import Depends
from models.artist import Artist
from models.song import Song
from repository.base_repository import ArtistRepository, _BaseG_Compatible, BaseRepository
from schemas.artist import ArtistSchema_Create, ArtistSchema_Read, ArtistSchema_Update
from services.base_service import CrudServiceBase

class CrudServiceArtist(CrudServiceBase):
    
    _repo:ArtistRepository
    def __init__(
        self, 
        artist_repo: Annotated[ArtistRepository, Depends(ArtistRepository)]
        ) -> None:
        super().__init__()
        self._repo = artist_repo
        
    def create(self, input_data: ArtistSchema_Create):
        dic = input_data.model_dump()
        input = {attribute: value for attribute, value in dic.items() 
                 if not isinstance(value, (list, set))}
        new_artist = Artist(**input)
        new_artist.songs.extend([Song(**s.model_dump()) for s in input_data.songs])
        new_id = self._repo.create(new_artist)
        return self.get_by_id(new_id, Artist)
    
    def update(self, id:int, updates:ArtistSchema_Update):
        old_artist = self.get_by_id(id, Artist)
        assert old_artist is not None
        return self._repo.update(instance=old_artist, updates=updates)