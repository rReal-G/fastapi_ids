from fastapi import APIRouter, HTTPException
# from repository.db_repository import get_db

from typing import Dict
from fastapi import Request, HTTPException
import logging
import requests
import secrets
from fastapi.responses import RedirectResponse
from oauthlib.oauth2 import WebApplicationClient
from services.G_oauth_service import G_Oauth_Svc

router = APIRouter(prefix='/account', 
                   tags=['account'],
                #    dependencies=[]
                   )


@router.get('/logout')
async def log_out(req:Request):
    req.session.clear()

@router.get("/login")
async def login(request: Request):
    oauth_client:WebApplicationClient = request.app.state.oauth_client
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

@router.get("/callbackG")
async def callback(req: Request):
    oauth_client:WebApplicationClient = req.app.state.oauth_client
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
    req.session[G_Oauth_Svc.G_ACCESS_TOKEN_SS_KEY] = access_token_dic

    userinfo_res = requests.get(
        G_Oauth_Svc.USERINFO_ENDPOINT, 
        headers = {'Authorization': f'Bearer {access_token}'},
        verify=False
        )
    if userinfo_res.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to obtain userinfo")
    user_json = userinfo_res.json()
    req.session[G_Oauth_Svc.G_USER_PROFILE_SS_KEY] = user_json
    return {"OG_G": access_token, 'userinfo': user_json}