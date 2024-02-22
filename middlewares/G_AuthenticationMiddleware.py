import logging
from typing import Annotated, Any, Coroutine
from fastapi import FastAPI, HTTPException, Header, Request, Response
import jwt
# from services.G_oauth_service import TokenBasedHandler
# from services.G_oauth_service import G_Oauth_Svc, UserInfo, AuthContext
import services.G_oauth_service as svc_G


class authentication_middleware_G(svc_G.G_Oauth_Svc):
    
    def __init__(self, app) -> None:
        super().__init__()
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope['path'] not in ['/login', '/callbackG', '/logout']:       
            req = Request(scope)            
            auth_head:str|None = req.headers.get('authorization')
            ctx = svc_G.AuthContext(req, scope, auth_head, self)
            
            token_handler = svc_G.TokenBasedHandler(ctx=ctx)
            cookie_handler = svc_G.CookieBasedHandler(ctx=ctx)
            token_handler.set_next(cookie_handler)
            await token_handler.handle()          
             
        await self.app(scope, receive, send)