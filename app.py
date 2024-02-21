import http
from fastapi import FastAPI, Request, HTTPException, Depends
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
from services.G_oauth_client import G_Oauth_Client

from utils.crypto import generate_code_pair

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="G rules")  
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(artist.router)
logging.basicConfig(level=logging.INFO)

@app.on_event('startup')
async def on_startup():
    ssl_context = ssl._create_unverified_context()
    app.state.aiohttp_session = aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl_context=ssl_context)
    )
    app.state.oauth_client = WebApplicationClient(G_Oauth_Client.CLIENT_ID)


@app.on_event('shutdown')
async def on_shutdown():
    await app.state.aiohttp_session.close()


@app.get('/')
async def root():
    return {'message': 'Hello World'}

@app.get('/logout')
async def log_out(req:Request):
    req.session.clear()

@app.get("/login")
async def login(request: Request):
    state = secrets.token_urlsafe(16)
    code_verifier, code_challenge = generate_code_pair()
    request.session['code_verifier'] = code_verifier
    request.session['state'] = state
    
    authorization_url = app.state.oauth_client.prepare_request_uri(
        uri=G_Oauth_Client.AUTH_ENDPOINT,
        redirect_uri=G_Oauth_Client.REDIRECT_URI,
        state=state,
        code_challenge=code_challenge,
        code_challenge_method='S256',
        scope=['testapi1', 'gg', 'openid', 'profile', 'offline_access'],
    )   
    return RedirectResponse(authorization_url)

@app.get("/callbackG")
async def callback(request: Request):
    access_token = request.session.get(G_Oauth_Client.G_ACCESS_TOKEN_KEY)
    if access_token:
        return {"G_ACCESS_TOKEN_KEY": access_token}
    
    code = request.query_params.get('code')
    state = request.query_params.get('state')
    if state != request.session.pop("state", None):
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    code_verifier = request.session.pop('code_verifier')
    token_url, headers, body = app.state.oauth_client.prepare_token_request(
        G_Oauth_Client.TOKEN_ENDPOINT, 
        code=code,
        redirect_url=G_Oauth_Client.REDIRECT_URI,
        code_verifier=code_verifier
        )
    response = requests.post(token_url, 
                             headers=headers, 
                             data=body, auth=(
                                 G_Oauth_Client.CLIENT_ID, 
                                 G_Oauth_Client.CLIENT_SECRET
                                ),
                            )

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to obtain tokens")
    
    json = response.json()
    access_token = json['access_token']

    request.session[G_Oauth_Client.G_ACCESS_TOKEN_KEY] = access_token

    return {"OG_G": access_token}







@app.get("/protected", dependencies=[Depends(G_Oauth_Client(
    required_scopes=['testapi1', 'gg'], audience=['G audience']
    ))])
async def protected():
    ...
    return {"message": "You've accessed a protected resource"}

@app.get('/call_remoted_protected')
async def call_remoted_protected_api(req:Request):
    access_token:str|None = req.session.get(G_Oauth_Client.G_ACCESS_TOKEN_KEY)
    if not access_token:
        return RedirectResponse('/login')
    url = 'https://localhost:7047/testidentity/get'
    async with app.state.aiohttp_session.get(url) as response:
        if response.status == 200:
            x = await response.text()
            return x
        else:
            print("Request failed:", response.status)
    

