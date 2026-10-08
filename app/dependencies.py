from typing import Annotated

import httpx
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.weather import WeatherService


DbSession = Annotated[
    AsyncSession,
    Depends(get_db),
]


def get_http_client(
    request: Request,
) -> httpx.AsyncClient:
    return request.app.state.http_client


HttpClient = Annotated[
    httpx.AsyncClient,
    Depends(get_http_client),
]


def get_weather_service(
    client: HttpClient,
) -> WeatherService:
    return WeatherService(client)


Weather = Annotated[
    WeatherService,
    Depends(get_weather_service),
]
