from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from db import database
from resources.routes import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await database.connect()

    yield

    # Shutdown
    await database.disconnect()


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
