from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from app.routers import cities, temperatures


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(
            10.0,
            connect=5.0,
        ),
    )

    yield

    await app.state.http_client.aclose()


app = FastAPI(
    title="City Temperature API",
    lifespan=lifespan,
)


app.include_router(cities.router)
app.include_router(temperatures.router)
