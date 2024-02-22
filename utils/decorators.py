import json
from oauthlib.common import generate_token
import functools
from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm.session import Session
import inspect
from repository.baseG_type import _BaseG_Compatible

class Utils_Decorators:

    @staticmethod
    def try_catch_wrap(f):
        @functools.wraps(f)
        async def wrapper(*a, **k):
            try:
                await f(*a, **k) if  inspect.iscoroutinefunction(f) else f(*a, **k)
            except Exception as e:
                raise HTTPException(500, detail=f'Not my fault: {str(e)}')
        return wrapper
        

    @staticmethod
    def require_scopes(required_scopes:list[str]):
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(req:Request, *args, **kw):
                from services.G_oauth_service import  UserInfo
                user_info:UserInfo = req.scope.get('userG', None)
                if not user_info:
                    return RedirectResponse('/login')
                allowed_scopes = user_info.allowed_scopes
                if [s for s in required_scopes if s not in user_info.allowed_scopes]:
                    raise HTTPException(403, 'missing scope')            
                return await func(req, *args, **kw)
            return wrapper
        return decorator            
    
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
        def wrapped(*args,**kw) ->  _BaseG_Compatible:
            db:Session = kw['db']
            instance:_BaseG_Compatible = kw['instance']
            new_artist = update_func(*args,**kw)
            db.merge(new_artist)
            db.commit()
            return instance
        return wrapped
    