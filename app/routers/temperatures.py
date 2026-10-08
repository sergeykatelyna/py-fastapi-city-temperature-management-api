from fastapi import APIRouter, HTTPException, status

from app import crud
from app import schemas
from app.dependencies import DbSession, Weather
from app.services.weather import WeatherServiceError


router = APIRouter(
    prefix="/temperatures",
    tags=["Temperatures"],
)


@router.post(
    "/update",
    response_model=list[schemas.Temperature],
)
async def update_temperatures(
    db: DbSession,
    weather: Weather,
):
    cities = await crud.get_cities(db)

    if not cities:
        return []

    try:
        readings = await weather.get_current_temperatures(
            cities,
        )

    except WeatherServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return await crud.create_temperature_records(
        db=db,
        readings=readings,
    )


@router.get(
    "",
    response_model=list[schemas.Temperature],
)
async def read_temperatures(
    db: DbSession,
    city_id: int | None = None,
):
    return await crud.get_temperatures(
        db=db,
        city_id=city_id,
    )
