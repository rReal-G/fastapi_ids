
import functools
from fastapi import HTTPException
from repository import base_repository
from sqlalchemy.orm.session import Session

class Repo_Deco:
    
    @staticmethod
    def toggle_raise_for_not_found(on:bool=False, detail:str=''):
        def decorator(repo_func):
            def wrapped(*args, **kw):
                res = repo_func(*args, **kw)
                if on and not res:
                    raise HTTPException(status_code=404, detail=detail)
                return res
            return wrapped
        return decorator
    
    @staticmethod
    def update_wrap(update_func):
        @functools.wraps(update_func)
        def wrapped(*args,**kw) ->  base_repository._BaseG_Compatible:
            db:Session = kw['db']
            instance: base_repository._BaseG_Compatible = kw['instance']
            new_artist = update_func(*args,**kw)
            db.merge(new_artist)
            db.commit()
            return instance
        return wrapped