import time
from typing import Annotated, Any, Callable, Coroutine
from fastapi import FastAPI, Request, HTTPException, Depends, Header
import requests
import jwt
import ssl
import logging

class G_Oauth_Client:
    CLIENT_ID = "fastapi client G"
    CLIENT_SECRET = "fastapi secret"
    IDS4_URL = 'https://localhost:7217'
    AUTH_ENDPOINT = f"{IDS4_URL}/connect/authorize"
    TOKEN_ENDPOINT = f"{IDS4_URL}/connect/token"
    REDIRECT_URI = 'http://localhost:8000/callbackG'
    WELL_KNOWN = f"{IDS4_URL}/.well-known/openid-configuration"
    G_ACCESS_TOKEN_KEY = 'G_ACCESS_TOKEN_KEY'

    @property
    def audience(self):
        return self._audience

    @audience.setter
    def audience(self, audience):
        self._audience = audience

    @property
    def required_scopes(self):
        return self._scopes

    @required_scopes.setter
    def required_scopes(self, audience):
        self._scopes = audience
    
    def __init__(
        self, *, 
        ssl_verify:bool=False, 
        required_scopes:list[str],
        audience:str|list[str] = 'fastapi client G') -> None:
        
        self.audience = audience
        self.required_scopes = required_scopes
        
        oidc_config = requests.get(G_Oauth_Client.WELL_KNOWN).json()
        self._ids4_signing_algos = oidc_config["id_token_signing_alg_values_supported"]
        jwks_client = jwt.PyJWKClient(oidc_config["jwks_uri"])
        if not ssl_verify:
            jwks_client.ssl_context = ssl._create_unverified_context()
        self._jwks_client = jwks_client

    @staticmethod
    def _time_wrap(f:Callable|Coroutine):
        async def wrapped(*a, **k):
            start = time.time()
            (await f(*a, **k)) if isinstance(f, Coroutine) else f(*a, **k)
            end = time.time()
            logging.log(logging.INFO, f'function {f.__name__}')
        return wrapped

            
    async def verify_token_G(self, access_token):      
        ids4_public_key = self._jwks_client.get_signing_key_from_jwt(access_token)
        og_decoded = jwt.decode(
            access_token,
            key=ids4_public_key.key, 
            algorithms=self._ids4_signing_algos,
            audience=self.audience
        )
        logging.log(logging.INFO, og_decoded)
        if [s for s in self.required_scopes if s not in og_decoded['scope']]:
            raise HTTPException(403, 'missing scope')

    #@_time_wrap
    async def __call__(self, authorization:Annotated[str|None, Header()]=None) -> Any:
        # auth_head = req.headers.get('Authorization')
        if not authorization:
            raise HTTPException(400, 'missing authorization header')
        access_token = authorization.split(' ')[-1]
        await self.verify_token_G(access_token)
    


    

