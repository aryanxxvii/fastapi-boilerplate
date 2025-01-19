from fastapi import FastAPI
from .routers.auth import auth_router
from .routers.files import files_router
from . import models
from .database import engine

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(files_router, prefix="/files", tags=["files"])