from pydantic import BaseModel
from datetime import date  
import schemas.song





class ArtistSchema_Create(BaseModel):
    created_at: date | None = None
    name: str 
    age: int 
    songs: list['schemas.song.SongSchema_Create'] = []    

class ArtistSchema_Read(ArtistSchema_Create):
    id: int
    songs: list['schemas.song.SongSchema_Read'] = [] 
    class Config:
        orm_omde = True 

class ArtistSchema_Update(ArtistSchema_Create):
    songs: list['schemas.song.SongSchema_Update_From_Artist'] = [] 