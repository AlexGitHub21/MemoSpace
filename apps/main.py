from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from apps import apps_router
import uvicorn

app = FastAPI()

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

app.include_router(router=apps_router)


def start():
    uvicorn.run(app="apps.main:app", reload=True)