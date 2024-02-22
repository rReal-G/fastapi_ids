from contextlib import asynccontextmanager
import functools
import http
from typing import Dict
from fastapi import FastAPI, Request, HTTPException, Depends
from middlewares.G_AuthenticationMiddleware import authentication_middleware_G
from routers import artist
import aiohttp
from fastapi.staticfiles import StaticFiles
import logging
import requests
import secrets
import hashlib
import base64 
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
app.add_middleware(SessionMiddleware, secret_key="G sekret")  
app.add_middleware(authentication_middleware_G)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(artist.router)
logging.basicConfig(level=logging.INFO)


@app.get('/')
async def root():
    return {'message': 'Hello World'}

@app.get('/logout')
async def log_out(req:Request):
    req.session.clear()

@app.get("/login")
async def login(request: Request):
    oauth_client:WebApplicationClient = app.state.oauth_client
    state = secrets.token_urlsafe(16)
    # code_verifier, code_challenge = generate_code_pair()
    code_verifier = oauth_client.create_code_verifier(69)
    code_challenge = oauth_client.create_code_challenge(code_verifier, 'S256')
    request.session['code_verifier'] = code_verifier
    request.session['state'] = state
    
    authorization_url = oauth_client.prepare_request_uri(
        uri=G_Oauth_Svc.AUTH_ENDPOINT,
        redirect_uri=G_Oauth_Svc.REDIRECT_URI,
        state=state,
        code_challenge=code_challenge,
        code_challenge_method='S256',
        scope=["user.profile.G", "who.am.i", "lmao.hehe", 
               "real.G", 'openid', 'profile', 'offline_access'],
    )   
    return RedirectResponse(authorization_url)

@app.get("/callbackG")
async def callback(req: Request):
    oauth_client:WebApplicationClient = app.state.oauth_client
    #alternative:
    # code = request.query_params.get('code')
    # state = request.query_params.get('state')
    # if state != request.session.pop("state", None):
    #     raise HTTPException(status_code=400, detail="Invalid state parameter")

    dic:Dict[str, str] = oauth_client.parse_request_uri_response(
        req.url._url, 
        state=req.session.pop("state", None)
        )
    logging.log(logging.INFO, dic)
    code = dic['code']
    code_verifier = req.session.pop('code_verifier')
    token_url, headers, body = oauth_client.prepare_token_request(
        G_Oauth_Svc.TOKEN_ENDPOINT, 
        code=code,
        redirect_url=G_Oauth_Svc.REDIRECT_URI,
        code_verifier=code_verifier,
        include_client_id=True,
        #client_id=G_Oauth_Svc.CLIENT_ID,
        client_secret=G_Oauth_Svc.CLIENT_SECRET
        )
    
    response = requests.post(token_url, headers=headers, data=body, verify=False)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to obtain tokens")
    
    json = response.json()
    id_token = json['id_token']
    access_token = json['access_token']
    expire_time = json['expires_in']
    refresh_token = json['refresh_token']
    access_token_dic = {'token': access_token, 'exp': expire_time, 'refresh': refresh_token}
    req.session[G_Oauth_Svc.G_ACCESS_TOKEN_KEY] = access_token_dic

    userinfo_res = requests.get(
        G_Oauth_Svc.USERINFO_ENDPOINT, 
        headers = {'Authorization': f'Bearer {access_token}'},
        verify=False
        )
    if userinfo_res.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to obtain userinfo")
    user_json = userinfo_res.json()
    return {"OG_G": access_token, 'userinfo': user_json}




# def require_scopes(required_scopes:list[str]):
#     def decorator(func):
#         @functools.wraps
#         async def wrapper(req:Request, *a, **k):
#             user_info:UserInfo = req.scope['userG']
#             allowed_scopes = user_info.allowed_scopes
#             if [s for s in required_scopes if s not in user_info.allowed_scopes]:
#                 raise HTTPException(403, 'missing scope')            
#             return await func()
#         return wrapper
#     return decorator



# @app.get("/protected", dependencies=[Depends(G_Oauth_Svc(
#     required_scopes=['testapi1', 'gg'], audience=['G audience']
#     ))])
@app.get('/protected', 
         dependencies=[Depends(G_Oauth_Svc.require_scopes(['real.G']))])
#@require_scopes(['real.G'])
async def protected(req: Request):
    ...
    return {
        "message": "You've accessed a protected resource",
        "detail": "required_scopes=['testapi1', 'gg'], audience=['G audience']"
            }


@app.get('/call_remoted_protected')
async def call_remoted_protected_api(req:Request):
    access_token:str|None = req.session.get(G_Oauth_Svc.G_ACCESS_TOKEN_KEY)
    if not access_token:
        return RedirectResponse('/login')
    url = 'https://localhost:7047/testidentity/get'
    async with app.state.aiohttp_session.get(url) as response:
        if response.status == 200:
            x = await response.json()
            return x
        else:
            print("Request failed:", response.status)
    

