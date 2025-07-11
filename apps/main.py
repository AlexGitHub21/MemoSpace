from fastapi import FastAPI
from apps import apps_router
import uvicorn

app = FastAPI()

app.include_router(router=apps_router)


def start():
    uvicorn.run(app="apps.main:app", reload=True)