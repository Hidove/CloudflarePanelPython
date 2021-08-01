
import uvicorn
from fastapi import FastAPI

from App import init_views, init_exception
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title='Hidove CloudFlare Panel', description='A Beautiful CloudFlare Partner Panel')
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_views(app)

init_exception(app)

if __name__ == '__main__':
    uvicorn.run(app='main:app', reload=False,host='0.0.0.0',port=8000)

