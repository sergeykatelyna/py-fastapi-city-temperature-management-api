from fastapi import APIRouter, HTTPException, Response, status

from app import crud
from app import schemas
from app.dependencies import DbSession, Weather
from app.services.weather import (
    CityNotFoundError,
    WeatherServiceError,
)


router = APIRouter(
    prefix="/cities",
    tags=["Cities"],
)


@router.post(
    "",
    response_model=schemas.City,
    status_code=status.HTTP_201_CREATED,
)
async def create_city(
    city: schemas.CityCreate,
    db: DbSession,
    weather: Weather,
):
    try:
        latitude, longitude = await weather.geocode_city(
            city.name,
        )

    except CityNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except WeatherServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return await crud.create_city(
        db=db,
        city=city,
        latitude=latitude,
        longitude=longitude,
    )


@router.get(
    "",
    response_model=list[schemas.City],
)
async def read_cities(
    db: DbSession,
):
    return await crud.get_cities(db)


@router.get(
    "/{city_id}",
    response_model=schemas.City,
)
async def read_city(
    city_id: int,
    db: DbSession,
):
    city = await crud.get_city(
        db=db,
        city_id=city_id,
    )

    if city is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found",
        )

    return city


@router.put(
    "/{city_id}",
    response_model=schemas.City,
)
async def update_city(
    city_id: int,
    city: schemas.CityUpdate,
    db: DbSession,
    weather: Weather,
):
    db_city = await crud.get_city(
        db=db,
        city_id=city_id,
    )

    if db_city is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found",
        )

    latitude = None
    longitude = None

    if city.name != db_city.name:
        try:
            latitude, longitude = (
                await weather.geocode_city(city.name)
            )

        except CityNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc

        except WeatherServiceError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=str(exc),
            ) from exc

    return await crud.update_city(
        db=db,
        db_city=db_city,
        city=city,
        latitude=latitude,
        longitude=longitude,
    )


@router.delete(
    "/{city_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_city(
    city_id: int,
    db: DbSession,
):
    db_city = await crud.get_city(
        db=db,
        city_id=city_id,
    )

    if db_city is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found",
        )

    await crud.delete_city(
        db=db,
        db_city=db_city,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
