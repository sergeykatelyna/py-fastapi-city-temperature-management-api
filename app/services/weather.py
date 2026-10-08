from datetime import datetime, timezone

import httpx


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


class WeatherServiceError(Exception):
    pass


class CityNotFoundError(WeatherServiceError):
    pass


class WeatherService:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    async def geocode_city(
        self,
        city_name: str,
    ) -> tuple[float, float]:
        try:
            response = await self.client.get(
                GEOCODING_URL,
                params={
                    "name": city_name,
                    "count": 1,
                    "language": "en",
                    "format": "json",
                },
            )

            response.raise_for_status()

        except httpx.TimeoutException as exc:
            raise WeatherServiceError(
                "Geocoding service timed out",
            ) from exc

        except httpx.HTTPError as exc:
            raise WeatherServiceError(
                "Geocoding service is unavailable",
            ) from exc

        data = response.json()
        results = data.get("results", [])

        if not results:
            raise CityNotFoundError(
                f"City '{city_name}' was not found",
            )

        result = results[0]

        return (
            float(result["latitude"]),
            float(result["longitude"]),
        )

    async def get_current_temperatures(
        self,
        cities: list,
    ) -> list[dict]:
        if not cities:
            return []

        latitude = ",".join(
            str(city.latitude)
            for city in cities
        )

        longitude = ",".join(
            str(city.longitude)
            for city in cities
        )

        try:
            response = await self.client.get(
                WEATHER_URL,
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": "temperature_2m",
                    "timezone": "UTC",
                    "timeformat": "iso8601",
                },
            )

            response.raise_for_status()

        except httpx.TimeoutException as exc:
            raise WeatherServiceError(
                "Weather service timed out",
            ) from exc

        except httpx.HTTPError as exc:
            raise WeatherServiceError(
                "Weather service is unavailable",
            ) from exc

        data = response.json()

        results = data if isinstance(data, list) else [data]

        if len(results) != len(cities):
            raise WeatherServiceError(
                "Weather service returned unexpected data",
            )

        readings = []

        for city, result in zip(cities, results):
            current = result.get("current")

            if not current:
                raise WeatherServiceError(
                    f"No current weather for city {city.id}",
                )

            timestamp = current.get("time")
            temperature = current.get("temperature_2m")

            if timestamp is None or temperature is None:
                raise WeatherServiceError(
                    f"Incomplete weather data for city {city.id}",
                )

            date_time = datetime.fromisoformat(
                timestamp.replace("Z", "+00:00"),
            )

            if date_time.tzinfo is None:
                date_time = date_time.replace(
                    tzinfo=timezone.utc,
                )

            readings.append(
                {
                    "city_id": city.id,
                    "date_time": date_time,
                    "temperature": float(temperature),
                }
            )

        return readings
