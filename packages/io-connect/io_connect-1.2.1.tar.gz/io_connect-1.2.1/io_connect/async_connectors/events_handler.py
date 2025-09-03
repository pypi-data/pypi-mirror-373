import asyncio
import logging
from datetime import datetime, timezone
from typing import Literal, Optional, Union

import aiohttp
import polars as pl
import pytz
from dateutil import parser
from typeguard import typechecked
import json
import io_connect.constants as c
from io_connect.async_connectors.file_logger import AsyncLoggerConfigurator
from io_connect.utilities.store import AsyncLogger


@typechecked
class AsyncEventsHandler:
    __version__ = c.VERSION

    # Class-level shared connection pool
    _shared_connector: Optional[aiohttp.TCPConnector] = None
    _connector_lock = asyncio.Lock()

    # Connection pool configuration (class-level, shared across all instances)
    # These can be modified directly: AsyncEventsHandler._pool_limit = 1000
    _pool_limit: int = 100  # Total connection pool size
    _pool_limit_per_host: int = 20  # Max connections per host
    _pool_keepalive_timeout: int = 30  # Keep connections alive (seconds)
    _pool_dns_cache_ttl: int = 300  # DNS cache TTL (seconds)

    # Timeout configuration (class-level, configurable)
    _default_timeout: int = 60  # Total request timeout in seconds
    _connect_timeout: int = 30  # Connection timeout in seconds

    def __init__(
        self,
        user_id: str,
        data_url: str,
        on_prem: Optional[bool] = False,
        tz: Optional[Union[pytz.BaseTzInfo, timezone]] = c.UTC,
        logger: Optional[
            Union[AsyncLogger, AsyncLoggerConfigurator, logging.Logger]
        ] = None,
        extra_params: Optional[dict] = None,
    ):
        """
        Initialize an AsyncEventsHandler instance for asynchronous event operations.

        Args:
            user_id (str): The API key or user ID for accessing the API.
            data_url (str): The URL of the data server.
            on_prem (Optional[bool], optional): Specifies whether the data server is on-premises. Defaults to False.
            tz (Optional[Union[pytz.BaseTzInfo, timezone]], optional): The timezone for timestamp conversions.
                    Accepts a pytz timezone object or a datetime.timezone object.
                    Defaults to UTC.
            logger (Optional[AsyncLogger], optional): Custom async logger instance. If None, a default logger is created.
            extra_params (Optional[dict], optional): Additional parameters for requests.

        Notes:
        -----
        - This is the asynchronous version of EventsHandler, all I/O operations must be awaited
        - Uses aiohttp for HTTP requests with shared connection pooling
        - All async methods should be called with await keyword
        """
        self.user_id = user_id
        self.data_url = data_url
        self.on_prem = on_prem
        self.tz = tz
        self.logger = logger if logger is not None else AsyncLogger()
        self.extra_params = extra_params or {}
        self.headers = {"userID": self.user_id}
        self.timeout = aiohttp.ClientTimeout(
            total=self._default_timeout, connect=self._connect_timeout
        )

    @classmethod
    async def _get_shared_connector(cls) -> aiohttp.TCPConnector:
        """
        Get or create a shared connection pool for all AsyncDataAccess instances.

        Returns:
            aiohttp.TCPConnector: Shared connector with configurable connection pooling
        """
        async with cls._connector_lock:
            # Check if connector exists and is healthy
            if cls._shared_connector is None or cls._shared_connector.closed:
                # Clean up old connector if it exists
                if cls._shared_connector is not None:
                    await cls._shared_connector.close()

                # Create new healthy connector
                cls._shared_connector = aiohttp.TCPConnector(
                    limit=cls._pool_limit,  # Total connection pool size
                    limit_per_host=cls._pool_limit_per_host,  # Max connections per host
                    ttl_dns_cache=cls._pool_dns_cache_ttl,  # DNS cache TTL
                    use_dns_cache=True,  # Enable DNS caching
                    keepalive_timeout=cls._pool_keepalive_timeout,  # Keep connections alive
                    enable_cleanup_closed=True,
                    force_close=False,  # Don't force close connections
                    ssl=False,  # Disable SSL verification for better reliability
                )
        return cls._shared_connector

    @classmethod
    async def cleanup_shared_connector(cls):
        """
        Clean up the shared connector. Call this when shutting down the application.
        """
        async with cls._connector_lock:
            if cls._shared_connector is not None:
                await cls._shared_connector.close()
                cls._shared_connector = None

    @classmethod
    async def refresh_shared_connector(cls):
        """
        Refresh the shared connector by closing and recreating it.
        Useful when connections are in a bad state.
        """
        async with cls._connector_lock:
            if cls._shared_connector is not None:
                await cls._shared_connector.close()
                cls._shared_connector = None
            # Next call to _get_shared_connector will create a new one

    def __iso_utc_time(self, time: Optional[Union[str, datetime]] = None) -> str:
        """
        Converts a given time to an ISO 8601 formatted string in UTC.
        If no time is provided, the current time in the specified timezone is used.
        Parameters:
        ----------
        time : Optional[Union[str, datetime]]
            The time to convert, which can be a string or a datetime object.
            If a string is provided, it will be parsed into a datetime object.
            If None is provided, the current time in the `self.tz` timezone will be used.
        Returns:
        -------
        str
            The time converted to an ISO 8601 formatted string in UTC.
        Raises:
        ------
        ValueError
            If there is a mismatch between the offset times of the provided time and `self.tz`.
        Notes:
        -----
        - If the provided time is a string, it will be parsed assuming the year comes first, followed by month and then year.
        - If the provided time does not have timezone information, it will be assumed to be in `self.tz` timezone.
        - The method ensures the time is converted to UTC before returning the ISO 8601 string.
        """
        # If time is not provided, use the current time in the specified timezone
        if time is None:
            return datetime.now(c.UTC).isoformat()

        if isinstance(time, str):
            time = parser.parse(time, dayfirst=False, yearfirst=True)

        # If the datetime object doesn't have timezone information, assume it's in self.tz timezone
        if time.tzinfo is None:
            if isinstance(self.tz, pytz.BaseTzInfo):
                # If tz is a pytz timezone, localize the datetime
                time = self.tz.localize(time)

            else:
                # If tz is a datetime.timezone object, replace tzinfo
                time = time.replace(tzinfo=self.tz)

        elif self.tz.utcoffset(time.replace(tzinfo=None)) != time.tzinfo.utcoffset(
            time
        ):
            raise ValueError(
                f"Mismatched offset times between time: ({time.tzinfo.utcoffset(time)}) and self.tz:({self.tz.utcoffset(time.replace(tzinfo=None))})"
            )

        # Return datetime object after converting to Unix timestamp
        return time.astimezone(c.UTC).isoformat()

    def time_to_unix(self, time: Optional[Union[str, int, datetime]] = None) -> int:
        """
        Convert a given time to Unix timestamp in milliseconds.

        Parameters:
        ----------
        time : Optional[Union[str, int, datetime]]
            The time to be converted. It can be a string in ISO 8601 format, a Unix timestamp in milliseconds, or a datetime object.
            If None, the current time in the specified timezone (`self.tz`) is used.

        Returns:
        -------
        int
            The Unix timestamp in milliseconds.

        Notes:
        -----
        - If `time` is not provided, the method uses the current time in the timezone specified by `self.tz`.
        - This method is kept synchronous as it only processes data locally.
        """
        # If time is not provided, use the current time in the specified timezone
        if time is None:
            return int(datetime.now(self.tz).timestamp() * 1000)

        # If time is already in Unix timestamp format
        if isinstance(time, int):
            if time <= 0 or len(str(time)) <= 10:
                raise ValueError(
                    "Unix timestamp must be a positive integer in milliseconds, not seconds."
                )
            return int(time)

        # If time is in string format, convert it to a datetime object
        if isinstance(time, str):
            time = parser.parse(time, dayfirst=False, yearfirst=True)

        # If the datetime object doesn't have timezone information, assume it's in self.tz timezone
        if time.tzinfo is None:
            if isinstance(self.tz, pytz.BaseTzInfo):
                # If tz is a pytz timezone, localize the datetime
                time = self.tz.localize(time)
            else:
                # If tz is a datetime.timezone object, replace tzinfo
                time = time.replace(tzinfo=self.tz)

        elif self.tz.utcoffset(time.replace(tzinfo=None)) != time.tzinfo.utcoffset(
            time
        ):
            raise ValueError(
                f"Mismatched offset times between time: ({time.tzinfo.utcoffset(time)}) and self.tz:({self.tz.utcoffset(time.replace(tzinfo=None))})"
            )

        # Return datetime object after converting to Unix timestamp
        return int(time.timestamp() * 1000)

    async def publish_event(
        self,
        message: str,
        meta_data: str,
        hover_data: str,
        created_on: Optional[str],
        event_tags_list: Optional[list] = None,
        event_names_list: Optional[list] = None,
        title: Optional[str] = None,
        on_prem: Optional[bool] = None,
    ) -> Optional[dict]:
        """
        Publish an event with the given details to the server asynchronously.

        Parameters:
        ----------
        message : str
            The main message or description of the event.

        meta_data : str
            Metadata associated with the event in string format.

        hover_data : str
            Data to be displayed when hovering over the event, in string format.

        created_on : Optional[str]
            The creation date of the event in string format. If not provided, the current date and time will be used.

        event_tags_list : Optional[list], default=None
            A list of pre-existing tags associated with the event. Either `event_tags_list` or `event_names_list` must be provided.

        event_names_list : Optional[list], default=None
            A list of human-readable names corresponding to event tags. These names are resolved into tag IDs using the `get_event_categories` method. Either `event_tags_list` or `event_names_list` must be provided.

        title : Optional[str], default=None
            The title of the event. If not provided, it will be set to None.

        on_prem : Optional[bool], default=None
            A flag indicating whether to publish the event to an on-premises server. If not provided, the default value from the class attribute (`self.on_prem`) will be used.

        Returns:
        -------
        Optional[dict]
            The response data from the server in dictionary format, or None if an error occurs.

        Raises:
        ------
        ValueError
            If any name in `event_names_list` does not have a corresponding tag ID.

        aiohttp.ClientError
            If there is an issue with the request to the server.

        Exception
            For other generic exceptions, such as missing tags when neither `event_tags_list` nor `event_names_list` is provided.

        Notes:
        -----
        - The method constructs the appropriate URL based on whether the event is being published to an on-premises server or a cloud server.
        - If `event_names_list` is provided, it resolves the names to tag IDs using the `get_event_categories` method.
        - If both `event_tags_list` and `event_names_list` are provided, only `event_names_list` will be used.
        - It prepares the request header and payload, then sends a POST request to the server.
        - The server's response is checked for success, and the data is returned if the request is successful.

        Example:
        -------
        >>> obj = EventsHandler(USER_ID, THIRD_PARTY_SERVER, ON_PREM, tz)
        >>> response = await obj.publish_event(
        ...     message="System update completed",
        ...     meta_data="{'version': '1.2.3', 'status': 'successful'}",
        ...     hover_data="Update was applied successfully without any issues.",
        ...     event_names_list=['System Update'],
        ...     created_on="2023-06-14T12:00:00Z",
        ...     title="System Update"
        ... )
        >>> print(response)
        {'eventId': '12345', 'status': 'published'}
        """
        try:
            # If on_prem is not provided, use the default value from the class attribute
            if on_prem is None:
                on_prem = self.on_prem

            if event_names_list:
                # Initialize event_tags_list as an empty list, as event_names_list will be used to populate it.
                event_tags_list = []

                # Fetch the available event categories from the server or a local method.
                data = await self.get_event_categories(on_prem=on_prem)

                # Iterate through each name in event_names_list to find its corresponding tag ID.
                for tag in event_names_list:
                    matched = next(
                        (item["_id"] for item in data if item["name"] == tag), None
                    )
                    # If no matching tag ID is found for the given name, raise an error.
                    if not matched:
                        raise ValueError(f"Tag '{tag}' not found in data.")
                    # Add the resolved tag ID to the event_tags_list.
                    event_tags_list.append(matched)

            # Ensure that at least one tag is present in event_tags_list after processing.
            if not event_tags_list:
                raise Exception("No event tags found.")

            # Construct the URL based on the on_prem flag
            protocol = "http" if on_prem else "https"
            url = c.PUBLISH_EVENT_URL.format(protocol=protocol, data_url=self.data_url)

            payload = {
                "title": title,
                "message": message,
                "metaData": meta_data,
                "eventTags": event_tags_list,
                "hoverData": hover_data,
                "createdOn": created_on,
            }

            session = None
            async with self.logger.timer("Publish Event:", self.extra_params):
                try:
                    # Use shared connector with proper session management
                    connector = await self._get_shared_connector()

                    session = aiohttp.ClientSession(
                        connector=connector,
                        timeout=self.timeout,
                        headers=self.headers,
                        connector_owner=False,  # Don't close the shared connector
                    )

                    async with session.post(url, json=payload, ssl=False) as response:
                        response.raise_for_status()
                        response_content = await response.json()

                    if "data" not in response_content:
                        raise aiohttp.ClientError("No data field in response")

                    return response_content["data"]

                finally:
                    # Always close the session to prevent resource leaks
                    if session and not session.closed:
                        await session.close()

        except aiohttp.ClientError as e:
            error_message = f"HTTPException: {e}"
            await self.logger.error(error_message, self.extra_params)
            return None

        except (ValueError, Exception) as e:
            error_message = f"Exception: {e}"
            await self.logger.error(error_message, self.extra_params)
            return None

    async def get_events_in_timeslot(
        self,
        start_time: Union[str, datetime],
        end_time: Optional[Union[str, datetime]] = None,
        on_prem: Optional[bool] = None,
    ) -> list:
        """
        Retrieves events within a specified time slot asynchronously.

        This method fetches events that occurred between the given start and end times.
        The times are converted to ISO 8601 formatted strings in UTC before making the request.
        The method handles both on-premises and third-party servers based on the `on_prem` flag.

        Parameters:
        ----------
        start_time : Union[str, datetime]
            The start time for the event search, in string or datetime format.
        end_time : Optional[Union[str, datetime]]
            The end time for the event search, in string or datetime format.
            If not provided, the current time is used.
        on_prem : Optional[bool]
            Flag indicating if the server is on-premises. If not provided,
            the class attribute `self.on_prem` is used.

        Returns:
        -------
        list
            A list of events found within the specified time slot.

        Raises:
        ------
        ValueError
            If the `end_time` is before the `start_time`.

        Notes:
        -----
        - The method constructs the request URL based on the `on_prem` flag.
        - The request header includes the user ID.
        - The response is checked for successful status, and the event data is extracted from the response.

        Exceptions:
        -----------
        - Handles `aiohttp.ClientError` to catch request-related errors.
        - Catches all other exceptions to prevent the program from crashing and logs the exception message.

        Example:
        -------
        >>> obj = EventsHandler(USER_ID, THIRD_PARTY_SERVER, ON_PREM, tz)
        >>> events = await obj.get_events_in_timeslot(start_time="2023-06-14T12:00:00Z")
        >>> print(events)
        [{'event_id': 1, 'timestamp': '2023-06-14T11:59:59Z', ...}, ...]
        """
        try:
            # Convert start_time and end_time to iso utc timestamps
            start_time_iso = self.__iso_utc_time(start_time)
            end_time_iso = self.__iso_utc_time(end_time)

            # Raise an error if end_time is before start_time
            if datetime.fromisoformat(end_time_iso) < datetime.fromisoformat(
                start_time_iso
            ):
                raise ValueError(
                    f"Invalid time range: start_time({start_time_iso}) should be before end_time({end_time_iso})."
                )

            # If on_prem is not provided, use the default value from the class attribute
            if on_prem is None:
                on_prem = self.on_prem

            # Construct the URL based on the on_prem flag
            protocol = "http" if on_prem else "https"
            url = c.GET_EVENTS_IN_TIMESLOT_URL.format(
                protocol=protocol, data_url=self.data_url
            )

            payload = {"startTime": start_time_iso, "endTime": end_time_iso}

            session = None
            async with self.logger.timer("Get Events In Timeslot:", self.extra_params):
                try:
                    # Use shared connector with proper session management
                    connector = await self._get_shared_connector()

                    session = aiohttp.ClientSession(
                        connector=connector,
                        timeout=self.timeout,
                        headers=self.headers,
                        connector_owner=False,  # Don't close the shared connector
                    )

                    async with session.put(url, json=payload, ssl=False) as response:
                        response.raise_for_status()
                        response_content = await response.json()

                    if "data" not in response_content:
                        raise aiohttp.ClientError("No data field in response")

                    return response_content["data"]

                finally:
                    # Always close the session to prevent resource leaks
                    if session and not session.closed:
                        await session.close()

        except aiohttp.ClientError as e:
            error_message = f"HTTPException: {e}"
            await self.logger.error(error_message, self.extra_params)
            return []

        except (ValueError, Exception) as e:
            error_message = f"Exception: {e}"
            await self.logger.error(error_message, self.extra_params)
            return []

    async def _get_paginated_data(self, url: str, payload: dict, parallel: bool):
        """
        Sends a PUT request to the specified API endpoint and processes the response asynchronously.

        Args:
            url (str): The API endpoint URL.
            payload (dict): The JSON payload to be sent in the request.
            parallel (bool): Determines whether to return only the "rows" field from the response data.

        Returns:
            dict: The processed response data. If `parallel` is True, returns only the "rows" field; otherwise, returns full data.

        Raises:
            aiohttp.ClientError: If the request fails or the response does not contain valid data.
            Exception: For any other unexpected errors.
        """
        try:
            session = None
            async with self.logger.timer("Paginated Data Request:", self.extra_params):
                try:
                    # Use shared connector with proper session management
                    connector = await self._get_shared_connector()

                    session = aiohttp.ClientSession(
                        connector=connector,
                        timeout=self.timeout,
                        headers=self.headers,
                        connector_owner=False,  # Don't close the shared connector
                    )

                    async with session.put(url, json=payload, ssl=False) as response:
                        response.raise_for_status()
                        response_content = await response.json()

                    data = response_content.get("data")

                    if data:
                        # If `parallel` is True, return only the "rows" field; otherwise, return the full data
                        return data.get("rows", {}) if parallel else data

                    # Raise an exception if the response does not contain the expected "data" field
                    raise aiohttp.ClientError("No data field in response")

                finally:
                    # Always close the session to prevent resource leaks
                    if session and not session.closed:
                        await session.close()

        except aiohttp.ClientError as e:
            error_message = f"HTTPException: {e}"
            await self.logger.error(error_message, self.extra_params)
            raise

        except Exception as e:
            error_message = f"Exception: {e}"
            await self.logger.error(error_message, self.extra_params)
            raise

    async def get_mongo_data(
        self,
        device_id: str,
        end_time: str,
        start_time: Optional[str] = None,
        limit: Optional[int] = None,
        alias: Optional[bool] = False,
        on_prem: Optional[bool] = None,
    ) -> pl.DataFrame:
        """
        Fetches data from the MongoDB for custom table Dev type for given device within a specified time range asynchronously.

        Parameters:
        - device_id (str): The ID of the device.
        - start_time (Optional[str]): The start time for data retrieval.
        - end_time (str): The end time for data retrieval.
        - limit (int): No of rows
        - alias (Optional[bool]): Whether to apply sensor aliasing. Defaults to False.
        - on_prem (Optional[bool]): Indicates if the operation is on-premise. Defaults to class attribute if not provided.

        Returns:
        - pl.DataFrame: The DataFrame containing the fetched and processed data.

        Exceptions Handled:
        - aiohttp.ClientError: Raised when there is an issue with the HTTP request.
        - Exception: General exception handling for other errors
        """
        try:
            if start_time and limit:
                raise Exception("Cannot process both start_time and limit.")

            # If on_prem is not provided, use the default value from the class attribute
            if on_prem is None:
                on_prem = self.on_prem
            # Determine the protocol based on the on_prem flag
            protocol = "http" if on_prem else "https"

            # Construct API URL for data retrieval
            url = c.GET_MONGO_DATA.format(protocol=protocol, data_url=self.data_url)

            # Prepare the payload
            payload = {
                "devID": device_id,
                "endTime": end_time,
                "rawData": True,
                **({"startTime": start_time} if start_time else {}),
                **({"limit": limit} if limit else {}),
            }

            if start_time:
                # Parse the response JSON
                data = await self._get_paginated_data(
                    url + "/1/500", payload, parallel=False
                )

                total_pages = data.get("totalPages", 0)
                initial_results = data.get("rows", [])

                # Use asyncio.gather for concurrent execution instead of ThreadPoolExecutor
                page_tasks = [
                    self._get_paginated_data(
                        url + f"/{page}/500", payload, parallel=True
                    )
                    for page in range(2, total_pages + 1)
                ]

                async with self.logger.timer(
                    "Parallel MongoDB Data Query:", self.extra_params
                ):
                    results = await asyncio.gather(*page_tasks, return_exceptions=True)

                # Filter out exceptions and add initial results
                valid_results = [
                    result for result in results if not isinstance(result, Exception)
                ]
                valid_results.append(initial_results)

                # Flatten results
                rows = [
                    row.get("data", {})
                    for page_rows in valid_results
                    for row in page_rows
                ]

            else:
                results = await self._get_paginated_data(url, payload, parallel=False)
                rows = [row["data"] for row in results]

            # Convert to DataFrame and sort
            df = pl.DataFrame(rows)

            if df.is_empty():
                return df

            # Sort by D0 column if it exists
            if "D0" in df.columns:
                df = df.sort("D0", descending=True)

            if alias:
                # Note: get_device_metadata needs to be implemented as async
                metadata = await self.get_device_metadata(
                    device_id=device_id, on_prem=on_prem
                )

                sensor_list = df.columns

                # Create a dictionary mapping sensor IDs to sensor names
                sensor_map = {
                    item["sensorId"]: "{} ({})".format(
                        item["sensorName"], item["sensorId"]
                    )
                    for item in metadata["sensors"]
                    if item["sensorId"] in sensor_list
                }

                # Rename the DataFrame columns using the constructed mapping
                df = df.rename(sensor_map)

            return df

        except Exception as e:
            error_message = f"Exception: {e}"
            await self.logger.error(error_message, self.extra_params)
            return pl.DataFrame()

    async def get_device_metadata(
        self, device_id: str, on_prem: Optional[bool] = None
    ) -> dict:
        """
        Fetches metadata for a specific device asynchronously.

        Args:
            device_id (str): The identifier of the device.
            on_prem (bool, optional): Specifies whether to use on-premises data server. If not provided, uses the class default.

        Returns:
            dict: Metadata for the specified device.

        Example:
            >>> events_handler = EventsHandler(user_id="my_user_id", data_url="data.url.com", ds_url="example_ds.com")
            >>> metadata = await events_handler.get_device_metadata(device_id="device123", on_prem=True)
            >>> print(metadata)
            {'id': 'device123', 'name': 'Device XYZ', 'location': 'Room A', ...}

        Raises:
            aiohttp.ClientError: If an error occurs during the HTTP request, such as a network issue or timeout.
            Exception: If an unexpected error occurs during metadata retrieval, such as parsing JSON data or other unexpected issues.
        """
        try:
            # If on_prem is not provided, use the default value from the class attribute
            if on_prem is None:
                on_prem = self.on_prem

            # Construct the URL based on the on_prem flag
            protocol = "http" if on_prem else "https"
            url = c.GET_DEVICE_METADATA_MONGO_URL.format(
                protocol=protocol, data_url=self.data_url
            )

            session = None
            async with self.logger.timer("Get Device Metadata:", self.extra_params):
                try:
                    # Use shared connector with proper session management
                    connector = await self._get_shared_connector()

                    session = aiohttp.ClientSession(
                        connector=connector,
                        timeout=self.timeout,
                        headers=self.headers,
                        connector_owner=False,  # Don't close the shared connector
                    )

                    async with session.get(
                        url + f"/{self.user_id}", params={"devID": device_id}, ssl=False
                    ) as response:
                        response.raise_for_status()
                        response_content = await response.json()

                    if "data" not in response_content:
                        raise aiohttp.ClientError("No data field in response")

                    return response_content["data"]

                finally:
                    # Always close the session to prevent resource leaks
                    if session and not session.closed:
                        await session.close()

        except aiohttp.ClientError as e:
            error_message = f"HTTPException: {e}"
            await self.logger.error(error_message, self.extra_params)
            return {}

        except (TypeError, ValueError) as e:
            error_message = f"Type Error: {type(e).__name__}: {e}"
            await self.logger.error(error_message, self.extra_params)
            return {}

        except Exception as e:
            error_message = f"Exception: {e}"
            await self.logger.error(error_message, self.extra_params)
            return {}

    async def get_event_categories(
        self,
        on_prem: Optional[bool] = None,
    ) -> list:
        """
        Retrieve a list of event categories from the server asynchronously.

        Parameters:
        ----------
        on_prem : Optional[bool]
            Flag indicating whether to use the on-premises server. If None, the default value from the class attribute `self.on_prem` is used.

        Returns:
        -------
        list
            A list of event categories.

        Raises:
        ------
        aiohttp.ClientError
            If there is an error with the HTTP request.

        Notes:
        -----
        - If `on_prem` is not provided, the method uses the class attribute `self.on_prem`.
        - The URL for the request is constructed based on the `on_prem` flag.
        - The method sends a GET request to the constructed URL with appropriate headers.
        - If the request is successful, the response is parsed from JSON to a list and returned.
        - If there is an exception during the request or other processing, an empty list is returned and the exception is logged to the console.

        Example:
        -------
        >>> obj = EventsHandler(USER_ID, THIRD_PARTY_SERVER, ON_PREM, tz)
        >>> categories = await obj.get_event_categories()
        >>> print(categories)
        ['Category1', 'Category2', 'Category3', ...]
        """
        try:
            # If on_prem is not provided, use the default value from the class attribute
            if on_prem is None:
                on_prem = self.on_prem

            # Construct the URL based on the on_prem flag
            protocol = "http" if on_prem else "https"
            url = c.GET_EVENT_CATEGORIES_URL.format(
                protocol=protocol, data_url=self.data_url
            )

            session = None
            async with self.logger.timer("Get Event Categories:", self.extra_params):
                try:
                    # Use shared connector with proper session management
                    connector = await self._get_shared_connector()

                    session = aiohttp.ClientSession(
                        connector=connector,
                        timeout=self.timeout,
                        headers=self.headers,
                        connector_owner=False,  # Don't close the shared connector
                    )

                    async with session.get(url, ssl=False) as response:
                        response.raise_for_status()
                        response_content = await response.json()

                    if "data" not in response_content:
                        raise aiohttp.ClientError("No data field in response")

                    return response_content["data"]

                finally:
                    # Always close the session to prevent resource leaks
                    if session and not session.closed:
                        await session.close()

        except aiohttp.ClientError as e:
            error_message = f"HTTPException: {e}"
            await self.logger.error(error_message, self.extra_params)
            return []

        except Exception as e:
            error_message = f"Exception: {e}"
            await self.logger.error(error_message, self.extra_params)
            return []

    async def get_detailed_event(
        self,
        event_tags_list: Optional[list] = None,
        start_time: Union[str, datetime] = None,
        end_time: Optional[Union[str, datetime]] = None,
        on_prem: Optional[bool] = None,
    ) -> list:
        """
        Retrieve detailed event data for a specified time range and event tags asynchronously.

        Parameters:
        ----------
        event_tags_list : Optional[list]
            A list of event tags to filter the events. If None, all event categories are considered.

        start_time : Union[str, datetime]
            The start time for fetching events. It can be a string in ISO 8601 format or a datetime object.

        end_time : Optional[Union[str, datetime]]
            The end time for fetching events. It can be a string in ISO 8601 format or a datetime object. If None, the current time is used.

        on_prem : Optional[bool]
            Flag indicating whether to use the on-premises server. If None, the default value from the class attribute `self.on_prem` is used.

        Returns:
        -------
        list
            A list of detailed event data records.

        Raises:
        ------
        aiohttp.ClientError
            If there is an error with the HTTP request.
        ValueError
            If the API response indicates a failure.

        Notes:
        -----
        - The method converts the provided `start_time` and `end_time` to ISO 8601 UTC timestamps.
        - If `on_prem` is not provided, the method uses the class attribute `self.on_prem`.
        - The URL for the request is constructed based on the `on_prem` flag.
        - The method sends a PUT request to the constructed URL with appropriate headers and payload to fetch event data in pages.
        - If there are more pages of data, the method fetches subsequent pages until all data is retrieved.
        - If there is an exception during the request or other processing, an empty list is returned and the exception is logged to the console.

        Example:
        -------
        >>> obj = EventsHandler(USER_ID, THIRD_PARTY_SERVER, ON_PREM, tz)
        >>> detailed_events = await obj.get_detailed_event(event_tags_list=['tag1', 'tag2'], start_time='2023-06-01T00:00:00Z')
        >>> print(detailed_events)
        [{'event_id': 1, 'timestamp': '2023-06-01T00:00:01Z', ...}, ...]

        """
        try:
            # Convert start_time and end_time to iso utc timestamps
            start_time_iso = self.__iso_utc_time(start_time)
            end_time_iso = self.__iso_utc_time(end_time)

            # If on_prem is not provided, use the default value from the class attribute
            if on_prem is None:
                on_prem = self.on_prem

            # Construct the URL based on the on_prem flag
            protocol = "http" if on_prem else "https"
            url = c.GET_DETAILED_EVENT_URL.format(
                protocol=protocol, data_url=self.data_url
            )

            # Retrieve event categories based on whether it's on-premises or not
            events = await self.get_event_categories(on_prem=on_prem)

            # Extract the IDs from the events
            id_list = [item["_id"] for item in events]

            # Check for event_tag
            if event_tags_list is None:
                tags = id_list
            else:
                # If event_tags_list is provided, find the intersection with id_list
                tags = list(set(event_tags_list).intersection(id_list))

            # Prepare the payload for the request
            payload = {
                "startTime": start_time_iso,
                "endTime": end_time_iso,
                "eventTags": tags,
                "count": 1000,
            }

            raw_data = []
            page = 1

            async with self.logger.timer("Get Detailed Event:", self.extra_params):
                # Loop to fetch data until there is no more data to fetch
                while True:
                    # Log the current page being fetched
                    await self.logger.info(
                        f"Fetching Data from page {page}", self.extra_params
                    )

                    session = None
                    try:
                        # Use shared connector with proper session management
                        connector = await self._get_shared_connector()

                        session = aiohttp.ClientSession(
                            connector=connector,
                            timeout=self.timeout,
                            headers=self.headers,
                            connector_owner=False,  # Don't close the shared connector
                        )

                        # Send a PUT request to fetch data from the current page
                        async with session.put(
                            url + f"/{page}/1000", json=payload, ssl=False
                        ) as response:
                            response.raise_for_status()
                            response_content = await response.json()

                        # Check for errors in the API response
                        if response_content.get("success") is False:
                            raise aiohttp.ClientError("API response indicates failure")

                        response_data = response_content["data"]["data"]
                        raw_data.extend(response_data)

                        page += 1  # Move to the next page

                        if len(raw_data) >= response_content["data"]["totalCount"]:
                            break  # Break the loop if no more data is available

                    finally:
                        # Always close the session to prevent resource leaks
                        if session and not session.closed:
                            await session.close()

            return raw_data

        except aiohttp.ClientError as e:
            error_message = f"HTTPException: {e}"
            await self.logger.error(error_message, self.extra_params)
            return []

        except Exception as e:
            error_message = f"Exception: {e}"
            await self.logger.error(error_message, self.extra_params)
            return []

    async def get_event_data_count(
        self,
        end_time: Optional[Union[str, datetime]] = None,
        count: Optional[int] = 10,
        on_prem: Optional[bool] = None,
    ) -> list:
        """
        Retrieve a specified number of event data records up to a given end time asynchronously.

        Parameters:
        ----------
        end_time : Optional[Union[str, datetime]]
            The end time up to which event data records are retrieved. It can be a string in ISO 8601 format or a datetime object.
            If None, the current time is used.

        count : Optional[int]
            The number of event data records to retrieve. The default value is 10. Must be less than 10,000.

        on_prem : Optional[bool]
            Flag indicating whether to use the on-premises server. If None, the default value from the class attribute self.on_prem is used.

        Returns:
        -------
        list
            A list of event data records.

        Raises:
        ------
        Exception
            If the count is greater than 10,000.
        aiohttp.ClientError
            If there is an error with the HTTP request.

        Notes:
        -----
        - The method converts the provided `end_time` to an ISO 8601 UTC timestamp.
        - If `on_prem` is not provided, the method uses the class attribute `self.on_prem`.
        - The URL for the request is constructed based on the `on_prem` flag.
        - The method sends a PUT request to the constructed URL with appropriate headers and payload.
        - If the request is successful, the response is parsed from JSON to a list and returned.
        - If there is an exception during the request or other processing, an empty list is returned and the exception is logged to the console.

        Example:
        -------
        >>> obj = EventsHandler(USER_ID, THIRD_PARTY_SERVER, ON_PREM, tz)
        >>> events = await obj.get_event_data_count('2023-06-14T12:00:00Z', count=5)
        >>> print(events)
        [{'event_id': 1, 'timestamp': '2023-06-14T11:59:59Z', ...}, ...]

        """
        try:
            if count > 10000:
                raise Exception("Count should be less than or equal to 10000.")

            # Convert end_time to iso utc timestamp
            end_time_iso = self.__iso_utc_time(end_time)

            # If on_prem is not provided, use the default value from the class attribute
            if on_prem is None:
                on_prem = self.on_prem

            # Construct the URL based on the on_prem flag
            protocol = "http" if on_prem else "https"
            url = c.GET_EVENT_DATA_COUNT_URL.format(
                protocol=protocol, data_url=self.data_url
            )

            payload = {"endTime": str(end_time_iso), "count": count}

            session = None
            async with self.logger.timer("Get Event Data Count:", self.extra_params):
                try:
                    # Use shared connector with proper session management
                    connector = await self._get_shared_connector()

                    session = aiohttp.ClientSession(
                        connector=connector,
                        timeout=self.timeout,
                        headers=self.headers,
                        connector_owner=False,  # Don't close the shared connector
                    )

                    async with session.put(url, json=payload, ssl=False) as response:
                        response.raise_for_status()
                        response_content = await response.json()

                    if "data" not in response_content:
                        raise aiohttp.ClientError("No data field in response")

                    return response_content["data"]

                finally:
                    # Always close the session to prevent resource leaks
                    if session and not session.closed:
                        await session.close()

        except aiohttp.ClientError as e:
            error_message = f"HTTPException: {e}"
            await self.logger.error(error_message, self.extra_params)
            return []

        except Exception as e:
            error_message = f"Exception: {e}"
            await self.logger.error(error_message, self.extra_params)
            return []

    async def get_device_data(
        self,
        devices: list = None,
        n: Optional[int] = 5000,
        end_time: Optional[str] = None,
        start_time: Optional[str] = None,
        on_prem: Optional[bool] = None,
    ) -> pl.DataFrame:
        """
        Fetch device data from the API with optional filters for time range and device list asynchronously.

        Args:
            devices (list, optional): List of device IDs to filter data for. Defaults to None (fetch all devices).
            n (int, optional): Maximum number of records to fetch. Defaults to 5000.
            end_time (str, optional): End time for the data range in ISO 8601 format. Defaults to None.
            start_time (str, optional): Start time for the data range in ISO 8601 format. Defaults to None.
            on_prem (bool, optional): Flag to indicate whether to use on-premise protocol ("http"). Defaults to None (uses "https").

        Returns:
            pl.DataFrame: A Polars DataFrame containing the flattened device data.
            If an exception occurs, an empty DataFrame is returned.
        """
        try:
            # If on_prem is not provided, use the default value from the class attribute
            if on_prem is None:
                on_prem = self.on_prem

            # Determine the protocol based on the on_prem flag
            protocol = "http" if on_prem else "https"

            # Prepare the payload for the request
            payload = {
                "devices": devices,
                "page": 1,
                "limit": n,
                "rawData": True,
            }
            if start_time:
                payload.update({"startTime": start_time})

            if end_time:
                payload.update({"endTime": end_time})

            # Construct API URL for data retrieval
            url = c.GET_DEVICE_DATA.format(protocol=protocol, data_url=self.data_url)

            session = None
            async with self.logger.timer("Get Device Data:", self.extra_params):
                try:
                    # Use shared connector with proper session management
                    connector = await self._get_shared_connector()

                    session = aiohttp.ClientSession(
                        connector=connector,
                        timeout=self.timeout,
                        headers=self.headers,
                        connector_owner=False,  # Don't close the shared connector
                    )

                    async with session.put(url, json=payload, ssl=False) as response:
                        response.raise_for_status()
                        response_content = await response.json()

                    if "error" in response_content:
                        raise aiohttp.ClientError("API response contains error")

                    device_data = response_content["rows"]
                    flat_data = []

                    # Flatten the device data for easier processing
                    for record in device_data:
                        flat_record = {"_id": record["_id"], "devID": record["devID"]}
                        # Include additional data fields from the record
                        flat_record.update(record["data"])
                        flat_data.append(flat_record)

                    # Convert the flattened data into a Polars DataFrame
                    df = pl.DataFrame(flat_data)

                    return df

                finally:
                    # Always close the session to prevent resource leaks
                    if session and not session.closed:
                        await session.close()

        except aiohttp.ClientError as e:
            error_message = f"HTTPException: {e}"
            await self.logger.error(error_message, self.extra_params)
            return pl.DataFrame()

        except Exception as e:
            error_message = f"Exception: {e}"
            await self.logger.error(error_message, self.extra_params)
            return pl.DataFrame()

    async def get_sensor_rows(
        self,
        device_id: Optional[str] = None,
        sensor: str = None,
        value: str = None,
        end_time: Optional[str] = None,
        start_time: Optional[str] = None,
        alias: Optional[bool] = False,
        on_prem: Optional[bool] = None,
    ) -> pl.DataFrame:
        """
        Retrieve device data rows from the server based on sensor parameters and optional time range filters asynchronously.

        This method queries the `TableDeviceRow` collection using the specified sensor key-value pair and time constraints.
        It constructs a GET request to the appropriate API endpoint and flattens the returned sensor data into a DataFrame.

        Parameters:
        ----------
        device_id : Optional[str], default=None
            The unique identifier of the device. If not provided, results may include multiple devices depending on server behavior.

        sensor : str
            The sensor key used to filter the data (e.g., 'temperature', 'humidity').

        value : str
            The expected value of the sensor to filter the records.

        end_time : Optional[str], default=None
            The end timestamp for the data range in ISO 8601 format (e.g., "2023-06-14T12:00:00Z"). If not provided, no upper bound is applied.

        start_time : Optional[str], default=None
            The start timestamp for the data range in ISO 8601 format. If not provided, no lower bound is applied.

        alias : Optional[bool], default=False
            Whether to apply sensor aliasing using device metadata. Defaults to False.

        on_prem : Optional[bool], default=None
            Whether to send the request to an on-premises server (`http`) or a cloud server (`https`).
            If not specified, the method uses the value of `self.on_prem`.

        Returns:
        -------
        pl.DataFrame
            A Polars DataFrame containing the flattened sensor data rows. If no data is returned or an error occurs, an empty DataFrame is returned.

        Raises:
        ------
        aiohttp.ClientError
            If the request fails or returns an error status code or malformed content.

        Exception
            For other unexpected exceptions encountered during execution.

        Notes:
        -----
        - Constructs the request payload with the specified filters and uses the appropriate server protocol.
        - Flattens nested sensor data for ease of use in downstream analysis or visualization.
        - Uses async session management with shared connectors for better performance.

        Example:
        -------
        >>> df = await events_handler.get_sensor_rows(
        ...     device_id="device123",
        ...     sensor="temperature",
        ...     value="25.3",
        ...     start_time="2023-06-14T10:00:00Z",
        ...     end_time="2023-06-14T12:00:00Z",
        ...     on_prem=True
        ... )
        >>> print(df.head())
        """
        try:
            # If on_prem is not provided, use the default value from the class attribute
            if on_prem is None:
                on_prem = self.on_prem

            # Determine the protocol based on the on_prem flag
            protocol = "http" if on_prem else "https"

            # Prepare the payload for the request
            payload = {"devID": device_id, "key": sensor, "value": value}
            if start_time:
                payload.update({"sTime": start_time})

            if end_time:
                payload.update({"eTime": end_time})

            # Construct API URL for data retrieval
            url = c.GET_SENSOR_ROWS.format(protocol=protocol, data_url=self.data_url)

            session = None
            async with self.logger.timer("Get Sensor Rows:", self.extra_params):
                try:
                    # Use shared connector with proper session management
                    connector = await self._get_shared_connector()

                    session = aiohttp.ClientSession(
                        connector=connector,
                        timeout=self.timeout,
                        headers=self.headers,
                        connector_owner=False,  # Don't close the shared connector
                    )

                    async with session.get(url, params=payload, ssl=False) as response:
                        response.raise_for_status()
                        response_content = await response.json()

                    if "error" in response_content:
                        raise aiohttp.ClientError("API response contains error")

                    device_data = response_content["data"]
                    flat_data = []

                    # Flatten the device data for easier processing
                    for record in device_data:
                        flat_record = {"_id": record["_id"], "devID": record["devID"]}
                        # Include additional data fields from the record
                        flat_record.update(record["data"])
                        flat_data.append(flat_record)

                    # Convert the flattened data into a Polars DataFrame
                    df = pl.DataFrame(flat_data)

                    if alias:
                        metadata = await self.get_device_metadata(
                            device_id=device_id, on_prem=on_prem
                        )

                        sensor_list = df.columns

                        # Create a dictionary mapping sensor IDs to sensor names
                        sensor_map = {
                            item["sensorId"]: "{} ({})".format(
                                item["sensorName"], item["sensorId"]
                            )
                            for item in metadata["sensors"]
                            if item["sensorId"] in sensor_list
                        }

                        # Rename the DataFrame columns using the constructed mapping
                        df = df.rename(sensor_map)

                    return df

                finally:
                    # Always close the session to prevent resource leaks
                    if session and not session.closed:
                        await session.close()

        except aiohttp.ClientError as e:
            error_message = f"HTTPException: {e}"
            await self.logger.error(error_message, self.extra_params)
            return pl.DataFrame()

        except Exception as e:
            error_message = f"Exception: {e}"
            await self.logger.error(error_message, self.extra_params)
            return pl.DataFrame()

    async def get_maintenance_module_data(
        self,
        start_time: Union[int, str, datetime],
        end_time: Optional[Union[int, str, datetime]] = None,
        remark_group: list = None,
        event_id: list = None,
        maintenance_module_id: str = None,
        operator: Literal["count", "activeDuration", "inactiveDuration"] = None,
        data_precision: int = None,
        periodicity: Optional[
            Literal["hour", "day", "week", "month", "quarter", "year"]
        ] = None,
        cycle_time: Optional[str] = None,
        week_start: Optional[int] = None,
        month_start: Optional[int] = None,
        year_start: Optional[int] = None,
        shifts: Optional[list] = None,
        shift_operator: Optional[
            Literal["sum", "mean", "median", "mode", "min", "max"]
        ] = None,
        filter: Optional[dict] = None,
        on_prem: Optional[bool] = None,
    ):
        """
        Fetch maintenance module data based on the provided parameters asynchronously.

        This function retrieves maintenance-related data from an API, transforming
        input parameters into a payload and handling the request-response cycle.

        Args:
            start_time (Union[int, str, datetime]): The start time of the query, as a Unix timestamp,
                ISO 8601 string, or a `datetime` object.
            end_time (Optional[Union[int, str, datetime]]): The end time of the query, optional.
            remark_group (list): A list of remark groups to filter by.
            event_id (list): A list of event IDs to include in the query.
            maintenance_module_id (str): The ID of the maintenance module to query.
            operator (Literal["count", "activeDuration", "inactiveDuration"]):
                The type of aggregation to apply to the data.
            data_precision (int): The precision for the returned data.
            periodicity (Optional[Literal["hour", "day", "week", "month", "quarter", "year"]]):
                The periodicity of the data (e.g., "day" for daily data).
            cycle_time (Optional[str]): The cycle time for calculating periodic data.
            week_start (Optional[int]): The starting day of the week (0 for Sunday, 1 for Monday).
            month_start (Optional[int]): The starting day of the month.
            year_start (Optional[int]): The starting month of the year.
            shifts (Optional[list]): A list of shifts to include in the query.
            shift_operator (Optional[Literal["sum", "mean", "median", "mode", "min", "max"]]):
                The aggregation operator to use for shifts.
            on_prem (Optional[bool]): Whether the API should use the on-premises protocol ("http")
                instead of cloud-based ("https").

        Returns:
            dict: The parsed response data from the API. If any errors occur, returns an empty dictionary.

        Raises:
            aiohttp.ClientError: If there is an error during the API request.
            Exception: If the API response contains errors or any other exception occurs.

        Example:
            data = await EventsHandler(USER_ID, DATA_URL).get_maintenance_module_data(
                start_time="2023-01-01T00:00:00Z",
                end_time="2023-01-31T23:59:59Z",
                operator="count",
                periodicity="day",
                remark_group=remark_group_list,
                event_id=event_id_list,
                maintenance_module_id=maintenance_module_id,
                operator="activeDuration",
                data_precision=2,
            )
        """
        try:
            # If on_prem is not provided, use the default value from the class attribute
            if on_prem is None:
                on_prem = self.on_prem

            # Determine the protocol based on the on_prem flag
            protocol = "http" if on_prem else "https"

            # Convert start_time and end_time to Unix timestamps
            start_time_unix = self.time_to_unix(start_time)
            end_time_unix = self.time_to_unix(end_time)

            # Validate that the start time is before the end time
            if end_time_unix < start_time_unix:
                raise ValueError(
                    f"Invalid time range: start_time({start_time}) should be before end_time({end_time})."
                )

            # Build the API payload with the required parameters
            payload = {
                "userID": self.user_id,
                "startTime": start_time_unix,
                "endTime": end_time_unix,
                "remarkGroup": remark_group,
                "eventID": event_id,
                "maintenanceModuleID": maintenance_module_id,
                "operator": operator,
                "timezone": str(self.tz),
                "dataPrecision": data_precision,
            }

            # Add periodicity and related parameters if specified
            if periodicity:
                payload.update(
                    {
                        "periodicity": periodicity,
                        "weekStart": week_start,
                        "monthStart": month_start,
                        "yearStart": year_start,
                        "eventID": event_id,
                    }
                )

            # Add cycle time to the payload if provided
            if cycle_time:
                payload.update({"cycleTime": cycle_time})

            # Add shift-related parameters if provided
            if shifts:
                payload.update({"shifts": shifts, "shiftOperator": shift_operator})

            if filter:
                payload.update({"filter": filter})

            # Construct API URL for data retrieval
            url = c.GET_MAINTENANCE_MODULE_DATA.format(
                protocol=protocol, data_url=self.data_url
            )

            session = None
            async with self.logger.timer(
                "Get Maintenance Module Data:", self.extra_params
            ):
                try:
                    # Use shared connector with proper session management
                    connector = await self._get_shared_connector()

                    session = aiohttp.ClientSession(
                        connector=connector,
                        timeout=self.timeout,
                        headers=self.headers,
                        connector_owner=False,  # Don't close the shared connector
                    )

                    async with session.put(url, json=payload, ssl=False) as response:
                        response.raise_for_status()
                        response_content = await response.json()

                    if "errors" in response_content:
                        raise aiohttp.ClientError("API response contains errors")

                    return response_content["data"]

                finally:
                    # Always close the session to prevent resource leaks
                    if session and not session.closed:
                        await session.close()

        except aiohttp.ClientError as e:
            error_message = f"HTTPException: {e}"
            await self.logger.error(error_message, self.extra_params)
            return {}

        except Exception as e:
            error_message = f"Exception: {e}"
            await self.logger.error(error_message, self.extra_params)
            return {}

    async def get_maintenance_module_filter(
        self,
        start_time: Union[int, str, datetime] = None,
        end_time: Optional[Union[int, str, datetime]] = None,
        events: list = None,
        module_id: str = None,
        oldest_first: Optional[Literal[1, -1]] = 1,
        limit: Optional[int] = 50,
        on_prem: Optional[bool] = None,
    ) -> list:
        """
        Asynchronously fetches maintenance module events within a specified time range.

        Args:
            start_time (int | str | datetime, optional): Start time of the query. Can be a UNIX timestamp, datetime object, or ISO 8601 string. Defaults to None.
            end_time (int | str | datetime, optional): End time of the query. Can be a UNIX timestamp, datetime object, or ISO 8601 string. Defaults to None.
            events (list, optional): List of event types to filter. Defaults to None (no event filtering).
            module_id (str, optional): Identifier of the maintenance module. Defaults to None.
            oldest_first (Literal[1, -1], optional): Sorting order of results.  
                1 → Ascending (oldest → latest).  
                -1 → Descending (latest → oldest).  
                Defaults to 1.
            limit (int, optional): Maximum number of records per page (max 50). Defaults to 50.
            on_prem (bool, optional): Specifies whether to use on-premises data server. If not provided, uses the class default.

        Returns:
            list: A list of maintenance module events matching the filters.

        Example:
            >>> events_handler = AsyncEventsHandler(user_id="my_user_id", data_url="data.url.com", ds_url="example_ds.com")
            >>> events = await events_handler.get_maintenance_module_filter(
            ...     start_time="2023-01-01T00:00:00Z",
            ...     end_time="2023-01-31T23:59:59Z",
            ...     events=["failure", "maintenance"],
            ...     module_id="module123",
            ...     oldest_first=-1,
            ...     limit=50,
            ...     on_prem=True
            ... )
            >>> print(events)
            [{'id': 'evt001', 'moduleId': 'module123', 'event': 'failure', 'timestamp': 1672531200, ...}, ...]

        Raises:
            ValueError: If the provided time range is invalid (start_time is after end_time).
            aiohttp.ClientError: If an error occurs during the HTTP request, such as a network issue or timeout.
            Exception: If an unexpected error occurs during data retrieval, such as parsing JSON data or other unexpected issues.
        """
        try:
            # Convert start_time and end_time to iso utc timestamps
            start_time_unix = self.time_to_unix(start_time)
            end_time_unix = self.time_to_unix(end_time)

            # Validate that the start time is before the end time
            if end_time_unix < start_time_unix:
                raise ValueError(
                    f"Invalid time range: start_time({start_time}) should be before end_time({end_time})."
                )

            # If on_prem is not provided, use the default value from the class attribute
            if on_prem is None:
                on_prem = self.on_prem

            # Construct the URL based on the on_prem flag
            protocol = "http" if on_prem else "https"
            url = c.GET_MAINTENANCE_MODULE_FILTER.format(
                protocol=protocol, data_url=self.data_url
            )
            payload = {
                "userId": self.user_id,
                "moduleId": module_id,
                "startTime": start_time_unix,
                "endTime": end_time_unix,
                "events": events,
                "sortOrder": oldest_first,
            }
            page = 0
            all_data = []

            async with self.logger.timer(
                "Get Maintenance Module Filter:", self.extra_params
            ):
                # Loop to fetch data until there is no more data to fetch
                while True:
                    # Log the current page being fetched
                    await self.logger.info(
                        f"Fetching Data from page {page}", self.extra_params
                    )

                    session = None
                    try:
                        # Use shared connector with proper session management
                        connector = await self._get_shared_connector()

                        session = aiohttp.ClientSession(
                            connector=connector,
                            timeout=self.timeout,
                            headers={
                                "Content-Type": "application/json",
                            },
                            connector_owner=False,  # Don't close the shared connector
                        )

                        # Send a PUT request to fetch data from the current page
                        async with session.put(
                            url + f"/{page}/{limit}",
                            data=json.dumps(payload),
                        ) as response:
                            response.raise_for_status()
                            response_content = await response.json()

                        # Check for errors in the API response
                        if "data" not in response_content:
                            raise aiohttp.ClientError("API response indicates failure")

                        data = response_content["data"]["data"]
                        total_count = response_content["data"]["totalCount"]
                        all_data.extend(data)

                        # Stop if we’ve fetched everything OR not in fetch_all mode
                        if len(all_data) >= total_count or not data:
                            break

                        # Increment skip for next page
                        page += 1

                    finally:
                        # Always close the session to prevent resource leaks
                        if session and not session.closed:
                            await session.close()

            return all_data

        except aiohttp.ClientError as e:
            error_message = f"HTTPException: {e}"
            await self.logger.error(error_message, self.extra_params)
            return []

        except Exception as e:
            error_message = f"Exception: {e}"
            await self.logger.error(error_message, self.extra_params)
            return []
