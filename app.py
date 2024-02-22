from contextlib import asynccontextmanager
import functools
import http
from typing import Any, Dict
from fastapi import FastAPI, Request, HTTPException, Depends
from middlewares.G_AuthenticationMiddleware import authentication_middleware_G
from routers import artist, account
import aiohttp
from fastapi.staticfiles import StaticFiles
import logging
import requests
import secrets
import hashlib
import base64 
from utils.decorators import Utils_Decorators
from fastapi.responses import RedirectResponse
from oauthlib.oauth2 import WebApplicationClient
from starlette.middleware.sessions import SessionMiddleware
import jwt
import ssl
from services.G_oauth_service import G_Oauth_Svc, UserInfo
from utils.crypto import generate_code_pair

@asynccontextmanager
async def your_entire_life(app:FastAPI):
    ssl_context = ssl._create_unverified_context()
    app.state.aiohttp_session = aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl_context=ssl_context)
    )
    app.state.oauth_client = WebApplicationClient(G_Oauth_Svc.CLIENT_ID)
    import os
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    yield
    await app.state.aiohttp_session.close()
    
app = FastAPI(lifespan=your_entire_life)
app.add_middleware(authentication_middleware_G)
app.add_middleware(SessionMiddleware, secret_key="G sekret")  
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(artist.router)
app.include_router(account.router)
logging.basicConfig(level=logging.INFO)


@app.get('/')
async def root(req:Request):
    return {'message': req.scope['userG']}

@app.get('/anon')
async def method_name(req:Request):
    return {
        "message": 'you are now anon',
        'req.session': req.session,
        'req.cookie': list(req.cookies.keys())
        }
# @app.get("/protected", dependencies=[Depends(G_Oauth_Svc(
#     required_scopes=['testapi1', 'gg'], audience=['G audience']
#     ))])

# @app.get('/protected', 
#          dependencies=[Depends(G_Oauth_Svc.require_scopes(['real.G']))])
@app.get('/protected')
@Utils_Decorators.require_scopes(['real.G']) #using this requires req:Request on every path func
async def protected(req:Request):
    ...
    user_info = req.scope.get('userG')
    return {
        "message": "You've accessed a protected resource",
        "user_info": user_info
        }


@app.get('/call_remoted_protected')
async def call_remoted_protected_api(req:Request):
    access_token:str|None = req.session.get(G_Oauth_Svc.G_ACCESS_TOKEN_SS_KEY)
    if not access_token:
        return RedirectResponse('/account/login')
    url = 'https://localhost:7047/testidentity/get'
    async with app.state.aiohttp_session.get(url) as response:
        if response.status == 200:
            x = await response.json()
            return x
        else:
            print("Request failed:", response.status)
    

