import requests
import pandas as pd
from pymongo import MongoClient
from typing import Dict
import urllib3
from typeguard import typechecked
import io_connect.constants as c

# Disable urllib3's warning about insecure requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

pd.options.mode.chained_assignment = None


@typechecked
class WeatherHandler:
    """
    A handler for fetching and storing weather data from APIs and MongoDB.

    Attributes:
        __version__ (str): The version of the WeatherHandler class.
        api_key (str): The API key for accessing weather data.
        db (MongoClient): The MongoDB client instance for database operations.
    """

    __version__ = c.VERSION

    def __init__(self, mongo_uri: str, database_name: str, api_key: str):
        """
        Initializes the WeatherHandler with MongoDB connection and API key.

        Args:
            mongo_uri (str): MongoDB connection URI.
            database_name (str): Name of the database to use.
            api_key (str): API key for weather data services.
        """
        self.api_key = api_key
        self.db = MongoClient(mongo_uri)[database_name]

    def get_weather_data(
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
            data = self.db[plant].find_one(
                {"lat": latitude, "lon": longitude, "date": date}
            )
            if data:
                return data

            # Fetch data from external weather API
            params = {
                "lat": latitude,
                "lon": longitude,
                "date": date,
                "appid": self.api_key,
            }

            # Make the request
            response = requests.get(
                c.WEATHER_API, params=params, verify=False, timeout=10
            )

            # Check the response status code
            response.raise_for_status()
            data = response.json()

            # Store the data in MongoDB
            self.db[plant].insert_one(data)
            return data

        except requests.exceptions.RequestException as e:
            print(f"[HTTP EXCEPTION] {type(e).__name__}: {e}")
            return {}

        except Exception as e:
            print(f"[EXCEPTION] {type(e).__name__}: {e}")
            return {}

    def get_weatherbit_data(
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
            data = self.db[plant].find_one(
                {"lat": latitude, "lon": longitude, "date": date}
            )
            if data:
                return data

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
            response = requests.get(
                c.WEATHERBIT_API, params=params, verify=False, timeout=10
            )

            # Check the response status code
            response.raise_for_status()
            data = response.json()

            if data:
                data["date"] = date
                data["lat"] = latitude
                data["lon"] = longitude

                # Store the data in MongoDB
                self.db[plant].insert_one(data)
                return data

        except requests.exceptions.RequestException as e:
            print(f"[HTTP EXCEPTION] {type(e).__name__}: {e}")
            return {}

        except Exception as e:
            print(f"[EXCEPTION] {type(e).__name__}: {e}")
            return {}
