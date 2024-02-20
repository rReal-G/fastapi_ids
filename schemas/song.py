from pydantic import BaseModel, Field
from datetime import date


class SongSchema_Create(BaseModel):
    created_at: date | None = None
    name: str
    #related_playlists: list[Playlist] = [] 

class SongSchema_Read(SongSchema_Create):
    id: int   
    artist_id:int
    
    class Config:
        orm_omde = True 

class SongSchema_Update_From_Artist(SongSchema_Create):
    id: int|None = None
    
