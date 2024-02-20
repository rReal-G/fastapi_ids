from turtle import title
from typing import Annotated, Sequence
from fastapi import APIRouter, Depends, Body, HTTPException
from models.artist import Artist
from models.song import Song
from repository.db_repository import get_db
import repository.db_repository as repo
from schemas.artist import ArtistSchema_Create, ArtistSchema_Read, ArtistSchema_Update
from sqlalchemy.orm.session import Session

from schemas.song import SongSchema_Create, SongSchema_Read

router = APIRouter(prefix='/artist', 
                   tags=['artist'],
                #    dependencies=[]
                   )

@router.get('/')
async def get_all_artists(db: Annotated[Session, Depends(get_db)]):
    artists = repo.read_all(db, Artist)
    artists_view = [
        ArtistSchema_Read.model_validate(a, from_attributes=True) 
        for a in artists
        ]
    return artists_view

@router.get('/{id}')
async def get_artist(id:int, 
                     db: Annotated[Session, Depends(get_db)]):
    artist = repo.read_by_id(db, id, Artist)
    if artist:
        artist_view = ArtistSchema_Read.model_validate(artist, from_attributes=True)
        return artist_view
    else:
        raise HTTPException(status_code=404, detail="artist not found")

@router.get('/{id}/songs')
async def get_artist_songs(id:int, 
                           db: Annotated[Session, Depends(get_db)]):
    artist = repo.read_by_id(db, id, Artist)
    if artist:
        songs = artist.songs
        songs_view = [SongSchema_Read.model_validate(s, from_attributes=True) for s in songs]
        return songs_view
    else:
        return []

@router.post('/create')
async def create_new_artist(artist: ArtistSchema_Create, 
                            db: Annotated[Session, Depends(get_db)]):
    dic = artist.dict()
    input = {
        attribute: value 
        for attribute, value in dic.items() 
        if not isinstance(value, (list, set))
        }
    new_artist = Artist(**input)
    new_artist.songs.extend([Song(**s.dict()) for s in artist.songs])
    # new_artist.songs.append(Song(artist.songs))
    x = repo.create(db, new_artist)
    res = ArtistSchema_Read.model_validate(x, from_attributes=True)
    return res

@router.post('/{id}/songs/add')
async def add_new_song(id:int, song_input: Annotated[SongSchema_Create, Body()], 
                            db: Annotated[Session, Depends(get_db)]):
    song = Song(**song_input.dict())
    artist = repo.read_by_id(db, id, Artist)
    if artist:
        artist.songs.append(song)
        db.commit()
        res = ArtistSchema_Read.model_validate(artist, from_attributes=True)
        return res
    else:
        raise HTTPException(status_code=404, detail="artist not found")

@router.put('/{id}/update')
async def update_artist(id:int, artist_changes: ArtistSchema_Update,
                        db: Annotated[Session, Depends(get_db)]):
    old_artist = repo.read_by_id(db, id, Artist)
    if old_artist:
        new_artist = repo.update(db, old_artist, artist_changes)
        return new_artist
    else:
        raise HTTPException(status_code=404, detail="artist not found")

@router.delete('/{id}')
async def delete_artist(id:int, 
                        db: Annotated[Session, Depends(get_db)]):
    to_be_erased = repo.read_by_id(db, id, Artist)
    if to_be_erased:
        erased = repo.delete(db, to_be_erased)
        artist_view = ArtistSchema_Read.model_validate(erased, from_attributes=True)
        return artist_view
    else:
        raise HTTPException(status_code=404, detail="artist not found")