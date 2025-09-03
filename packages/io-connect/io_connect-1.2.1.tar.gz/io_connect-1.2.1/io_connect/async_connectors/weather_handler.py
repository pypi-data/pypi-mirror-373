import aiohttp
import asyncio
import pandas as pd
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict
from typeguard import typechecked
import io_connect.constants as c

# Disable chained assignment warnings for pandas
pd.options.mode.chained_assignment = None


@typechecked
class AsyncWeatherHandler:
    """
    An async handler for fetching and storing weather data from APIs and MongoDB.

    Attributes:
        __version__ (str): The version of the AsyncWeatherHandler class.
        api_key (str): The API key for accessing weather data.
        db (AsyncIOMotorClient): The async MongoDB client instance for database operations.
    """

    __version__ = c.VERSION

    def __init__(self, mongo_uri: str, database_name: str, api_key: str):
        """
        Initializes the AsyncWeatherHandler with MongoDB connection and API key.

        Args:
            mongo_uri (str): MongoDB connection URI.
            database_name (str): Name of the database to use.
            api_key (str): API key for weather data services.
        """
        self.api_key = api_key
        self.db = AsyncIOMotorClient(mongo_uri)[database_name]
        self._session = None

    async def __aenter__(self):
        """
        Async context manager entry - creates HTTP session.
        """
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Async context manager exit - closes HTTP session.
        """
        await self.close()

    async def _ensure_session(self):
        """
        Ensures that an HTTP session exists.
        """
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(ssl=False)
            timeout = aiohttp.ClientTimeout(total=10)
            self._session = aiohttp.ClientSession(connector=connector, timeout=timeout)

    async def close(self):
        """
        Closes the HTTP session gracefully.
        """
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def get_weather_data(
        self, plant: str, date: str, latitude: float, longitude: float
    ) -> Dict:
        """
        Fetches weather data for a specific plant and date. Checks MongoDB first,
        and if not found, fetches from the external weather API and stores it in MongoDB.

        Args:
            plant (str): The name of the plant (used as the collection name).
            date (str): The target date for weather data in YYYY-MM-DD format.
            latitude (float): Latitude of the location.
            longitude (float): Longitude of the location.

        Returns:
            Dict: Weather data as a dictionary. Returns an empty dictionary on failure.
        """
        try:
            # Check MongoDB for existing data
            data = await self.db[plant].find_one(
                {"lat": latitude, "lon": longitude, "date": date}
            )
            if data:
                return data

            await self._ensure_session()

            # Fetch data from external weather API
            params = {
                "lat": latitude,
                "lon": longitude,
                "date": date,
                "appid": self.api_key,
            }

            # Make the request
            async with self._session.get(c.WEATHER_API, params=params) as response:
                # Check the response status code
                response.raise_for_status()
                data = await response.json()

            # Store the data in MongoDB
            await self.db[plant].insert_one(data)
            return data

        except aiohttp.ClientError as e:
            print(f"[HTTP EXCEPTION] {type(e).__name__}: {e}")
            return {}

        except Exception as e:
            print(f"[EXCEPTION] {type(e).__name__}: {e}")
            return {}

    async def get_weatherbit_data(
        self, plant: str, date: str, hour: int, latitude: float, longitude: float
    ) -> Dict:
        """
        Fetches weather data from the Weatherbit API for a specific plant and time.
        Checks MongoDB first, and if not found, fetches from the Weatherbit API and stores it.

        Args:
            plant (str): The name of the plant (used as the collection name).
            date (str): The target date for weather data in YYYY-MM-DD format.
            hour (int): The hour for which data is needed.
            latitude (float): Latitude of the location.
            longitude (float): Longitude of the location.

        Returns:
            Dict: Weather data as a dictionary. Returns an empty dictionary on failure.
        """
        try:
            # Check MongoDB for existing data
            data = await self.db[plant].find_one(
                {"lat": latitude, "lon": longitude, "date": date}
            )
            if data:
                return data

            await self._ensure_session()

            # Fetch data from external weather API
            params = {
                "lat": latitude,
                "lon": longitude,
                "key": self.api_key,
                "hours": hour,
                "units": "M",
                "lang": "en",
            }

            # Make the request
            async with self._session.get(c.WEATHERBIT_API, params=params) as response:
                # Check the response status code
                response.raise_for_status()
                data = await response.json()

            if data:
                data["date"] = date
                data["lat"] = latitude
                data["lon"] = longitude

                # Store the data in MongoDB
                await self.db[plant].insert_one(data)
                return data

        except aiohttp.ClientError as e:
            print(f"[HTTP EXCEPTION] {type(e).__name__}: {e}")
            return {}

        except Exception as e:
            print(f"[EXCEPTION] {type(e).__name__}: {e}")
            return {}

    def __del__(self):
        """
        Destructor to ensure session is closed.
        """
        if self._session and not self._session.closed:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.close())
                else:
                    loop.run_until_complete(self.close())
            except:
                pass  # Ignore errors during cleanup 