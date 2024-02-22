import logging
from typing import Annotated, Any, Coroutine
from fastapi import FastAPI, HTTPException, Header, Request, Response
import jwt

from services.G_oauth_service import G_Oauth_Svc, UserInfo

# async def authentication_middleware_G(request: Request, call_next):
#     # Logic before processing the request
#     start_time = time.time()  

#     response = await call_next(request)

#     # Logic after processing the request
#     process_time = time.time() - start_time
#     print(f"Request path: {request.url.path}, Process time: {process_time:.2f}s")

#     return response

class authentication_middleware_G(G_Oauth_Svc):
    
    def __init__(self, app:FastAPI) -> None:
        super().__init__()
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope['path'] not in ['/login', '/callbackG']:       
            req = Request(scope)            
            auth_head:str|None = req.headers.get('authorization')
            if not auth_head:
                raise HTTPException(400, 'missing authorization header')
            access_token = auth_head.split(' ')[-1]
            ids4_public_key = self._jwks_client.get_signing_key_from_jwt(access_token)
            og_decoded = jwt.decode(
                access_token,
                key=ids4_public_key.key, 
                algorithms=self._ids4_signing_algos,
                audience=self.audience
            )
            logging.log(logging.INFO, og_decoded)
            # if [s for s in self.required_scopes if s not in og_decoded['scope']]:
            #     raise HTTPException(403, 'missing scope')
            allowed_scopes = og_decoded['scope']
            sub = og_decoded['sub']
            scope['userG'] = UserInfo(sub, allowed_scopes)
        await self.app(scope, receive, send)