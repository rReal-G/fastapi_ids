from turtle import title
from typing import Annotated, Sequence
from fastapi import APIRouter, Depends, Body, HTTPException
from models.artist import Artist
from models.song import Song
# from repository.db_repository import get_db
import repository.base_repository as repo
from schemas.artist import ArtistSchema_Create, ArtistSchema_Read, ArtistSchema_Update
from sqlalchemy.orm.session import Session

from schemas.song import SongSchema_Create, SongSchema_Read
from services.artist_service import CrudServiceArtist
from services.base_service import CrudServiceBase

router = APIRouter(prefix='/artist', 
                   tags=['artist'],
                #    dependencies=[]
                   )

@router.get('/')
async def get_all_artists(crud_svc: Annotated[CrudServiceBase, Depends(CrudServiceArtist)]):
    artists = crud_svc.get_all(Artist)
    artists_view = [ArtistSchema_Read.model_validate(a, from_attributes=True) 
                    for a in artists]
    return artists_view

@router.get('/{id}')
async def get_artist(crud_svc: Annotated[CrudServiceBase, Depends(CrudServiceArtist)], 
                            id: int):
    artist = crud_svc.get_by_id(id, Artist)
    artist_view = ArtistSchema_Read.model_validate(artist, from_attributes=True)
    return artist_view


# @router.get('/{id}/songs')
# async def get_artist_songs(id:int, 
#                            db: Annotated[Session, Depends(get_db)]):
#     artist = repo.read_by_id(db, id, Artist)
#     if artist:
#         songs = artist.songs
#         songs_view = [SongSchema_Read.model_validate(s, from_attributes=True) for s in songs]
#         return songs_view
#     else:
#         return []

@router.post('/create')
async def create_new_artist(crud_svc: Annotated[CrudServiceBase, Depends(CrudServiceArtist)], 
                            artist_input: ArtistSchema_Create):
    created_model = crud_svc.create(artist_input)
    return ArtistSchema_Read.model_validate(created_model, from_attributes=True)


# @router.post('/{id}/songs/add')
# async def add_new_song(id:int, song_input: Annotated[SongSchema_Create, Body()], 
#                             db: Annotated[Session, Depends(get_db)]):
#     song = Song(**song_input.dict())
#     artist = repo.read_by_id(db, id, Artist)
#     if artist:
#         artist.songs.append(song)
#         db.commit()
#         res = ArtistSchema_Read.model_validate(artist, from_attributes=True)
#         return res
#     else:
#         raise HTTPException(status_code=404, detail="artist not found")


@router.put('/{id}/update')
async def update_artist(crud_svc: Annotated[CrudServiceBase, Depends(CrudServiceArtist)], 
                        updates: ArtistSchema_Create, id:int):
    updated_artist = crud_svc.update(id, updates)
    return ArtistSchema_Read.model_validate(updated_artist, from_attributes=True)

@router.delete('/{id}')
async def delete_artist(crud_svc: Annotated[CrudServiceBase, Depends(CrudServiceArtist)], 
                        id: int):
    erased = crud_svc.delete(id, Artist)
    artist_view = ArtistSchema_Read.model_validate(erased, from_attributes=True)
    return artist_view
