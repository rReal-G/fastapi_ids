from dataclasses import dataclass, field
import inspect
import time
from typing import Annotated, Any, Callable, Coroutine, Dict
import aiohttp
from fastapi import FastAPI, Request, HTTPException, Depends, Header
import requests
import jwt
import ssl
import logging
from typing import Protocol

class AuthContext(Protocol):
    req:Request
    auth_header:str|None 
    
class AuthHandlerProtocol(Protocol):
    _next:'AuthHandlerProtocol|None'
    def __init__(self, next_handler:'AuthHandlerProtocol|None'=None, 
                 *, context:AuthContext):
        self._next = next_handler
    def set_next(self, next_handler:'AuthHandlerProtocol') -> None:
        self._next = next_handler
    def call_next(self, ctx:AuthContext):
        if self._next:
            return self._next.handle(ctx)
    def handle(self, ctx:AuthContext) -> Any:
        ...
        
     

class TokenBasedHandler(AuthHandlerProtocol):   
    def handle(self, ctx:AuthContext):
        ...
        
class CookieBasedHandler(AuthHandlerProtocol):
    def handle(self, ctx:AuthContext):
        ...

@dataclass
class UserInfo:
    sub:str
    allowed_scopes:list[str] = field(default_factory = lambda: [])
    userprofile:Dict[str, str] = field(default_factory = lambda: {})



class G_Oauth_Svc:
    CLIENT_ID = "fastapi client G"
    CLIENT_SECRET = "fastapi secret"
    IDS4_URL = 'https://localhost:7217'
    AUTH_ENDPOINT = f"{IDS4_URL}/connect/authorize"
    TOKEN_ENDPOINT = f"{IDS4_URL}/connect/token"
    USERINFO_ENDPOINT = f"{IDS4_URL}/connect/userinfo"
    WELL_KNOWN_ENDPOINT = f"{IDS4_URL}/.well-known/openid-configuration"
    REDIRECT_URI = 'http://localhost:8000/callbackG'
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
        required_scopes:list[str] = [],
        audience:str|list[str] = 'G audience'
        ) -> None:
        
        self.audience = audience
        self.required_scopes = required_scopes
        # async with aiohttp.ClientSession(connector = \
        #     aiohttp.TCPConnector(ssl_context=ssl._create_unverified_context())) as cs:
        #     async with cs.get(G_Oauth_Client.WELL_KNOWN) as wellknown_res:
        #         oidc_config = await wellknown_res.json()
        oidc_config = requests.get(G_Oauth_Svc.WELL_KNOWN_ENDPOINT, verify=False).json()
        self._ids4_signing_algos = oidc_config["id_token_signing_alg_values_supported"]
        jwks_client = jwt.PyJWKClient(oidc_config["jwks_uri"])
        if not ssl_verify:
            jwks_client.ssl_context = ssl._create_unverified_context()
        self._jwks_client = jwks_client

    @staticmethod
    def _time_wrap(f:Callable|Coroutine):
        async def wrapped(*a, **k):
            start = time.time()
            G = (await f(*a, **k)) if inspect.iscoroutinefunction(f) else  f(*a, **k) #type:ignore
            end = time.time()
            logging.log(logging.INFO, f'function {f.__name__} took {start-end} to complete')
            return G
        return wrapped

    @_time_wrap
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
    

    @staticmethod
    def require_scopes(required_scopes:list[str]):
        async def wrapper(req:Request):
            user_info:UserInfo = req.scope['userG']
            allowed_scopes = user_info.allowed_scopes
            if [s for s in required_scopes if s not in user_info.allowed_scopes]:
                raise HTTPException(403, 'missing scope')            
        return wrapper

    

