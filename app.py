from fastapi import FastAPI
from routers import artist

app = FastAPI()


app.include_router(artist.router)

@app.get('/')
async def root():
    return {'message': 'Hello World'}
