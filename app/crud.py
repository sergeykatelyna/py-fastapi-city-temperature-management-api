from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app import schemas


async def create_city(
    db: AsyncSession,
    city: schemas.CityCreate,
    latitude: float,
    longitude: float,
) -> models.City:
    db_city = models.City(
        **city.model_dump(),
        latitude=latitude,
        longitude=longitude,
    )

    db.add(db_city)
    await db.commit()
    await db.refresh(db_city)

    return db_city


async def get_city(
    db: AsyncSession,
    city_id: int,
) -> models.City | None:
    return await db.get(models.City, city_id)


async def get_cities(
    db: AsyncSession,
) -> list[models.City]:
    statement = (
        select(models.City)
        .order_by(models.City.id)
    )

    result = await db.scalars(statement)

    return result.all()


async def update_city(
    db: AsyncSession,
    db_city: models.City,
    city: schemas.CityUpdate,
    latitude: float | None = None,
    longitude: float | None = None,
) -> models.City:
    db_city.name = city.name
    db_city.additional_info = city.additional_info

    if latitude is not None:
        db_city.latitude = latitude

    if longitude is not None:
        db_city.longitude = longitude

    await db.commit()
    await db.refresh(db_city)

    return db_city


async def delete_city(
    db: AsyncSession,
    db_city: models.City,
) -> None:
    await db.delete(db_city)
    await db.commit()


async def get_temperatures(
    db: AsyncSession,
    city_id: int | None = None,
) -> list[models.Temperature]:
    statement = (
        select(models.Temperature)
        .order_by(models.Temperature.date_time.desc())
    )

    if city_id is not None:
        statement = statement.where(
            models.Temperature.city_id == city_id
        )

    result = await db.scalars(statement)

    return result.all()


async def create_temperature_records(
    db: AsyncSession,
    readings: list[dict],
) -> list[models.Temperature]:
    temperature_records = [
        models.Temperature(**reading)
        for reading in readings
    ]

    db.add_all(temperature_records)

    await db.commit()

    return temperature_records
