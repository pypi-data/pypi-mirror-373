import asyncio
import logging
from datetime import datetime, timezone
from operator import itemgetter
from typing import Dict, List, Literal, Optional, Tuple, Union

import aiohttp
import polars as pl
import pytz
from dateutil import parser
from typeguard import typechecked

import io_connect.constants as c
from io_connect.async_connectors.file_logger import AsyncLoggerConfigurator
from io_connect.utilities.store import AsyncLogger


@typechecked
class AsyncDataAccess:
    __version__ = c.VERSION

    # Class-level shared connection pool
    _shared_connector: Optional[aiohttp.TCPConnector] = None
    _connector_lock = asyncio.Lock()

    # Connection pool configuration (class-level, shared across all instances)
    # These can be modified directly: AsyncDataAccess._pool_limit = 1000
    _pool_limit: int = 200  # Total connection pool size
    _pool_limit_per_host: int = 50  # Max connections per host
    _pool_keepalive_timeout: int = 30  # Keep connections alive (seconds)
    _pool_dns_cache_ttl: int = 300  # DNS cache TTL (seconds)

    def __init__(
        self,
        user_id: str,
        data_url: str,
        ds_url: str,
        on_prem: Optional[bool] = False,
        tz: Optional[Union[pytz.BaseTzInfo, timezone]] = c.UTC,
        logger: Optional[
            Union[AsyncLogger, AsyncLoggerConfigurator, logging.Logger]
        ] = None,
        extra_params: Optional[dict] = {},
    ):
        """
        Initialize an AsyncDataAccess instance for asynchronous sensor data operations.

        Args:
            user_id (str): The API key or user ID for accessing the API.
            data_url (str): The URL of the data server.
            ds_url (str): The URL of the data source.
            on_prem (Optional[bool], optional): Specifies whether the data server is on-premises. Defaults to False.
            tz (Optional[Union[pytz.BaseTzInfo, timezone]], optional): The timezone for timestamp conversions.
                    Accepts a pytz timezone object or a datetime.timezone object.
                    Defaults to UTC.
            logger (Optional[Union[AsyncLogger, AsyncLoggerConfigurator, logging.Logger]], optional): Custom logger instance. If None, a default AsyncLogger is created.
            extra_params (Optional[dict], optional): Additional parameters for requests.

        Notes:
        -----
        - This is the asynchronous version of DataAccess, all I/O operations must be awaited
        - Uses aiohttp for HTTP requests instead of requests library
        - Metadata must be pre-fetched for calibration and alias operations
        - All async methods should be called with await keyword
        """
        self.user_id = user_id
        self.data_url = data_url
        self.ds_url = ds_url
        self.on_prem = on_prem
        self.tz = tz
        self.logger = logger if logger is not None else AsyncLogger()
        self.extra_params = extra_params
        self.headers = {"userID": self.user_id}
        self.timeout = aiohttp.ClientTimeout(total=60, connect=30)

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

    @staticmethod
    def _ensure_consistent_numeric_types(
        df: pl.DataFrame, batch_df: pl.DataFrame
    ) -> tuple[pl.DataFrame, pl.DataFrame]:
        """
        Ensure consistent numeric types for all overlapping numeric columns.
        Returns (df, batch_df) with aligned dtypes.
        """
        if not df.is_empty() and not batch_df.is_empty():
            for col in batch_df.columns:
                if col in df.columns and col != "time":
                    if df[col].dtype.is_numeric() and batch_df[col].dtype.is_numeric():
                        # Force both sides to Float64
                        df = df.with_columns(pl.col(col).cast(pl.Float64))
                        batch_df = batch_df.with_columns(pl.col(col).cast(pl.Float64))
        return df, batch_df

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

    async def get_user_info(self, on_prem: Optional[bool] = None) -> dict:
        """
        Fetches user information from the API asynchronously.

        Args:
            on_prem (bool, optional): Specifies whether to use on-premises data server. If not provided, uses the class default.

        Returns:
            dict: A dictionary containing user information.

        Example:
            >>> data_access = AsyncDataAccess(user_id="my_user_id", data_url="data.url.com", ds_url="example_ds.com")
            >>> user_info = await data_access.get_user_info(on_prem=True)
            >>> print(user_info)

        Raises:
            aiohttp.ClientError: If an error occurs during the HTTP request, such as a network issue or timeout.
            Exception: If an unexpected error occurs during metadata retrieval, such as parsing JSON data or other unexpected issues.
        """
        # If on_prem is not provided, use the default value from the class attribute
        if on_prem is None:
            on_prem = self.on_prem

        # Construct the URL based on the on_prem flag
        protocol = "http" if on_prem else "https"
        url = c.GET_USER_INFO_URL.format(protocol=protocol, data_url=self.data_url)

        async with self.logger.timer("User Info Query:", self.extra_params):
            session = None
            try:
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
                    await self.logger.error(
                        "User data not available!", self.extra_params
                    )
                    return {}
                return response_content["data"]

            except aiohttp.ClientError as e:
                error_message = f"HTTPException: {e}"
                await self.logger.error(error_message, self.extra_params)
                return {}

            except (TypeError, ValueError) as e:
                error_message = f"Type Error: {type(e).__name__}: {e}"
                await self.logger.error(error_message, self.extra_params)
                return {}

            except Exception as e:
                error_message = f"Unexpected Exception: {e}"
                await self.logger.critical(error_message, self.extra_params)
                return {}
            finally:
                # Always close the session to prevent resource leaks
                if session and not session.closed:
                    await session.close()

    async def get_device_details(self, on_prem: Optional[bool] = None) -> pl.DataFrame:
        """
        Fetch details of all devices from the API asynchronously.

        Args:
            on_prem (bool, optional): Specifies whether to use on-premises data server. If not provided, uses the class default.

        Returns:
            pl.DataFrame: DataFrame containing details of all devices.

        Example:
            >>> data_access = AsyncDataAccess(user_id="my_user_id", data_url="data.url.com", ds_url="example_ds.com")
            >>> device_details_df = await data_access.get_device_details(on_prem=True)
            >>> print(device_details_df)

        Raises:
            aiohttp.ClientError: If an error occurs during the HTTP request, such as a network issue or timeout.
            Exception: If an unexpected error occurs during metadata retrieval, such as parsing JSON data or other unexpected issues.
        """
        if on_prem is None:
            on_prem = self.on_prem

        # Construct the URL based on the on_prem flag
        protocol = "http" if on_prem else "https"
        url = c.GET_DEVICE_DETAILS_URL.format(protocol=protocol, data_url=self.data_url)

        async with self.logger.timer("Device Details Query:", self.extra_params):
            session = None
            try:
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
                    await self.logger.error("Devices not available!", self.extra_params)
                    return pl.DataFrame()

                return pl.DataFrame(response_content["data"])

            except aiohttp.ClientError as e:
                error_message = f"HTTPException: {e}"
                await self.logger.error(error_message, self.extra_params)
                return pl.DataFrame()

            except (TypeError, ValueError) as e:
                error_message = f"Type Error: {type(e).__name__}: {e}"
                await self.logger.error(error_message, self.extra_params)
                return pl.DataFrame()

            except Exception as e:
                error_message = f"Unexpected Exception: {e}"
                await self.logger.critical(error_message, self.extra_params)
                return pl.DataFrame()
            finally:
                # Always close the session to prevent resource leaks
                if session and not session.closed:
                    await session.close()

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
            >>> data_access = AsyncDataAccess(user_id="my_user_id", data_url="data.url.com", ds_url="example_ds.com")
            >>> metadata = await data_access.get_device_metadata(device_id="device123", on_prem=True)
            >>> print(metadata)
            {'id': 'device123', 'name': 'Device XYZ', 'location': 'Room A', ...}

        Raises:
            aiohttp.ClientError: If an error occurs during the HTTP request, such as a network issue or timeout.
            Exception: If an unexpected error occurs during metadata retrieval, such as parsing JSON data or other unexpected issues.
        """
        if on_prem is None:
            on_prem = self.on_prem

        # Construct the URL based on the on_prem flag
        protocol = "http" if on_prem else "https"
        url = c.GET_DEVICE_METADATA_URL.format(
            protocol=protocol, data_url=self.data_url, device_id=device_id
        )

        async with self.logger.timer("Device Metadata Query:", self.extra_params):
            session = None
            try:
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
                    await self.logger.error(
                        "Device Metadata not available!", self.extra_params
                    )
                    return {}
                return response_content["data"]

            except aiohttp.ClientError as e:
                error_message = f"HTTPException: {e}"
                await self.logger.error(error_message, self.extra_params)
                return {}

            except (TypeError, ValueError) as e:
                error_message = f"Type Error: {type(e).__name__}: {e}"
                await self.logger.error(error_message, self.extra_params)
                return {}

            except Exception as e:
                error_message = f"Unexpected Exception: {e}"
                await self.logger.critical(error_message, self.extra_params)
                return {}
            finally:
                # Always close the session to prevent resource leaks
                if session and not session.closed:
                    await session.close()

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

        Raises:
        ------
        ValueError
            If the provided Unix timestamp is not in milliseconds or if there are mismatched offset times between `time` timezone and `self.tz`.

        Notes:
        -----
        - If `time` is not provided, the method uses the current time in the timezone specified by `self.tz`.
        - If `time` is already in Unix timestamp format (in milliseconds), it is validated and returned directly.
        - If `time` is provided as a string, it is parsed into a datetime object.
        - If the datetime object doesn't have timezone information, it is assumed to be in the timezone specified by `self.tz`.
        - The method ensures consistency in timezone information between `time` and `self.tz` before converting to Unix timestamp.
        - Unix timestamps must be provided in milliseconds format (> 10 digits).

        Example:
        -------
        >>> data_access = AsyncDataAccess(user_id="my_user_id", data_url="data.url.com", ds_url="example_ds.com")
        >>> unix_time = data_access.time_to_unix('2023-06-14T12:00:00Z')
        >>> print(unix_time)
            1686220800000
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

    def __get_cleaned_table(
        self,
        df: pl.DataFrame,
        alias: bool,
        cal: bool,
        device_id: str,
        sensor_list: list,
        on_prem: bool,
        unix: bool,
        metadata: Optional[dict] = None,
        pivot_table: Optional[bool] = True,
    ) -> pl.DataFrame:
        """
        Clean and preprocess a DataFrame containing time-series sensor data.

        Parameters:
        ----------
        df : pl.DataFrame
            The input DataFrame containing sensor data with columns 'time', 'sensor', and 'value'.

        alias : bool
            Flag indicating whether to apply sensor aliasing based on device configuration.

        cal : bool
            Flag indicating whether to apply calibration to sensor values.

        device_id : str
            The identifier for the device from which sensor data is collected.

        sensor_list : list
            A list of sensor IDs or names to filter and process from the DataFrame.

        on_prem : bool
            Flag indicating whether the data is retrieved from an on-premises server or not.

        unix : bool
            Flag indicating whether to convert 'time' column to Unix timestamp format in milliseconds.

        metadata : Optional[dict], default=None
            Additional metadata related to sensors or calibration parameters.

        pivot_table : Optional[bool], default=True
            Flag indicating whether to pivot the DataFrame to have sensors as columns.

        Returns:
        -------
        pl.DataFrame
            A cleaned and preprocessed DataFrame with columns adjusted based on the provided parameters.

        Notes:
        -----
        - The method assumes the input DataFrame (`df`) has columns 'time', 'sensor', and 'value'.
        - It converts the 'time' column to datetime format and sorts the DataFrame by 'time'.
        - The DataFrame is pivoted to have sensors as columns, indexed by 'time'.
        - Sensor list is filtered to include only sensors present in the DataFrame.
        - Calibration (`cal=True`) adjusts sensor values based on calibration parameters fetched from the server.
        - Sensor aliasing (`alias=True`) replaces sensor IDs or names with user-friendly aliases.
        - If `unix=True`, the 'time' column is converted to Unix timestamp format in milliseconds.
        - Timezone conversion is applied to 'time' column if `unix=False`, using the timezone (`self.tz`) specified during class initialization.
        - The method returns the cleaned and processed DataFrame suitable for further analysis or export.
        - This method is kept synchronous as it only processes data locally.
        """

        if pivot_table:
            # Ensure time column is in datetime format
            df = df.with_columns(
                [
                    pl.col("time")
                    .str.strptime(pl.Datetime, format=None, strict=False)
                    .alias("time")
                ]
            )
            df = df.sort("time")

            # Pivot DataFrame without cross-sensor fill
            df = df.pivot(values="value", index="time", columns="sensor")

            # Filter sensor list to include only present sensors
            available_columns = df.columns
            sensor_list = [
                sensor for sensor in sensor_list if sensor in available_columns
            ]

        # Apply calibration if required
        if cal:
            df, metadata = self.__get_calibration(
                device_id=device_id,
                sensor_list=sensor_list,
                metadata=metadata,
                df=df,
                on_prem=on_prem,
            )

        # Apply sensor alias if required
        if alias:
            df, metadata = self.get_sensor_alias(
                device_id=device_id,
                df=df,
                sensor_list=sensor_list,
                on_prem=on_prem,
                metadata=metadata,
            )

        # Convert time to Unix timestamp if required
        if unix:
            df = df.with_columns(
                [
                    pl.col("time")
                    .map_elements(
                        lambda x: int(x.timestamp() * 1000), return_dtype=pl.Int64
                    )
                    .alias("time")
                ]
            )
        else:
            # Convert time column to timezone
            df = df.with_columns(
                [pl.col("time").dt.convert_time_zone(str(self.tz)).alias("time")]
            )

        return df

    def get_sensor_alias(
        self,
        device_id: str,
        df: pl.DataFrame,
        on_prem: Optional[bool] = None,
        sensor_list: Optional[list] = None,
        metadata: Optional[dict] = None,
    ) -> Tuple[pl.DataFrame, Dict]:
        """
        Applies sensor aliasing to the DataFrame columns.

        This method retrieves sensor aliases from metadata and renames DataFrame columns
        accordingly, appending the sensor ID to the alias for clarity.

        Args:
            device_id (str): The ID of the device.
            df (pl.DataFrame): DataFrame containing sensor data.
            on_prem (bool): Whether the data is on-premise.
            sensor_list (list): List of sensor IDs.
            metadata (Optional[dict]): Metadata containing sensor information.

        Example:
            >>> data_access = AsyncDataAccess(user_id="my_user_id", data_url="data.url.com", ds_url="example_ds.com")
            >>> metadata = await data_access.get_device_metadata("TEST_DEVICE")
            >>> device_details_df, metadata = data_access.get_sensor_alias(df=df, device_id="TEST_DEVICE", metadata=metadata)
            >>> print(device_details_df)

        Returns:
            pl.DataFrame: DataFrame with renamed columns.
            dict: Updated metadata with sensor information.

        Notes:
        -----
        - This method is kept synchronous as it only processes data locally.
        - For the async version, metadata must be pre-fetched asynchronously before calling this method.
        """
        # If on_prem is not provided, use the default value from the class attribute
        if on_prem is None:
            on_prem = self.on_prem

        # If metadata is not provided, it should be fetched asynchronously before calling this method
        if metadata is None:
            raise ValueError("Metadata must be provided for async version")

        if sensor_list is None:
            sensor_list = df.columns

        # Create a dictionary mapping sensor IDs to sensor names
        sensor_map = {
            item["sensorId"]: "{} ({})".format(item["sensorName"], item["sensorId"])
            for item in metadata["sensors"]
            if item["sensorId"] in sensor_list
        }

        # Rename the DataFrame columns using the constructed mapping
        df = df.rename(sensor_map)

        return df, metadata

    def __get_calibration(
        self,
        device_id: str,
        sensor_list: list,
        df: pl.DataFrame,
        on_prem: bool = False,
        metadata: Optional[dict] = None,
    ) -> Tuple[pl.DataFrame, Dict]:
        """
        Applies calibration to sensor data in the DataFrame.

        This method extracts calibration parameters from metadata and applies them to the
        corresponding sensor data in the DataFrame.

        Args:
            device_id (str): The ID of the device.
            sensor_list (list): List of sensor IDs.
            df (pl.DataFrame): DataFrame containing sensor data.
            on_prem (bool): Whether the data is on-premise. Defaults to False.
            metadata (Optional[dict]): Metadata containing calibration parameters.

        Returns:
            pl.DataFrame: DataFrame with calibrated sensor data.
            dict: Updated metadata with calibration information.

        Notes:
        -----
        - This method is kept synchronous as it only processes data locally.
        - For the async version, metadata must be pre-fetched asynchronously before calling this method.
        """
        # If metadata is not provided, it should be fetched asynchronously before calling this method
        if metadata is None:
            raise ValueError("Metadata must be provided for async version")

        # Define default calibration values
        default_values = {"m": 1.0, "c": 0.0, "min": float("-inf"), "max": float("inf")}

        # Extract sensor calibration data from metadata
        data = metadata.get("params", {})

        # Iterate over sensor_list to apply calibration
        for sensor in sensor_list:
            if sensor not in df.columns:
                continue

            # Extract calibration parameters for the current sensor
            params = {
                param["paramName"]: param["paramValue"]
                for param in data.get(sensor, [])
            }
            cal_values = {}

            # Populate cal_values with extracted parameters or defaults if not available
            for key in default_values:
                try:
                    cal_values[key] = float(params.get(key, default_values[key]))
                except Exception:
                    cal_values[key] = default_values[key]

            if cal_values != default_values:
                # Apply calibration using polars
                df = df.with_columns(
                    [
                        pl.col(sensor)
                        .cast(pl.Float64, strict=False)
                        .map_elements(
                            lambda x: max(
                                min(
                                    cal_values["m"] * x + cal_values["c"],
                                    cal_values["max"],
                                ),
                                cal_values["min"],
                            )
                            if x is not None
                            else None,
                            return_dtype=pl.Float64,
                        )
                        .alias(sensor)
                    ]
                )

        return df, metadata

    async def get_dp(
        self,
        device_id: str,
        sensor_list: Optional[List] = None,
        n: int = 1,
        cal: Optional[bool] = True,
        end_time: Optional[Union[str, int, datetime]] = None,
        alias: Optional[bool] = False,
        unix: Optional[bool] = False,
        on_prem: Optional[bool] = None,
    ) -> pl.DataFrame:
        """
        Retrieve and process data points (DP) from sensors for a given device asynchronously.

        Args:
            device_id (str): The ID of the device.
            sensor_list (Optional[List], optional): List of sensor IDs. If None, all sensors for the device are used.
            end_time (Optional[Union[str, int, datetime]], optional): The end time for data retrieval.
                Defaults to None.
            n (int, optional): Number of data points to retrieve. Defaults to 1.
            cal (bool, optional): Whether to apply calibration. Defaults to True.
            alias (bool, optional): Whether to apply sensor aliasing. Defaults to False.
            unix (bool, optional): Whether to return timestamps in Unix format. Defaults to False.
            on_prem (Optional[bool], optional): Whether the data source is on-premise.
                If None, the default value from the class attribute is used. Defaults to None.

        Returns:
            pl.DataFrame: DataFrame containing retrieved and processed data points.

        Example:
            >>> data_access = AsyncDataAccess(user_id="my_user_id", data_url="data.url.com", ds_url="example_ds.com")
            >>> df = await data_access.get_dp("XYZ",sensor_list= ['X'],n=1,alias=True,cal=True,end_time=1685767732710,unix=False)
            >>> print(df)

        Raises:
            ValueError: If parameter 'n' is less than 1.
            Exception: If no sensor data is available.
            Exception: If max retries for data fetching from api-layer are exceeded.
            TypeError: If an unexpected type error occurs during execution.
            aiohttp.ClientError: If an error occurs during HTTP request.
            Exception: For any other unexpected exceptions raised during execution.
        """
        try:
            metadata = None
            # Validate input parameters
            if n < 1:
                raise ValueError("Parameter 'n' must be greater than or equal to 1")

            df_devices = await self.get_device_details(on_prem=on_prem)

            # Check if the device is added in the account
            if device_id not in df_devices["devID"].to_list():
                raise Exception(f"Message: Device {device_id} not added in account")

            need_metadata = sensor_list is None or cal or alias
            if need_metadata:
                # Fetch metadata if sensor_list is not provided
                metadata = await self.get_device_metadata(device_id, on_prem)

                if sensor_list is None:
                    sensor_list = list(map(itemgetter("sensorId"), metadata["sensors"]))

                # Ensure sensor_list is not empty
                if not sensor_list:
                    raise Exception("No sensor data available.")

            # Convert end_time to Unix timestamp
            end_time = self.time_to_unix(end_time)

            # If on_prem is not provided, use the default value from the class attribute
            if on_prem is None:
                on_prem = self.on_prem
            protocol = "http" if on_prem else "https"

            # Construct API URL for data retrieval
            url = c.GET_DP_URL.format(protocol=protocol, data_url=self.data_url)

            # Process all sensors concurrently for better performance
            sensor_tasks = [
                self._fetch_sensor_data(url, device_id, sensor, end_time, n)
                for sensor in sensor_list
            ]

            async with self.logger.timer("Get DP Query:", self.extra_params):
                # Execute all sensor data fetches concurrently
                sensor_results = await asyncio.gather(
                    *sensor_tasks, return_exceptions=True
                )

            # Combine all results, filtering out exceptions
            df = pl.DataFrame()
            for result in sensor_results:
                if isinstance(result, pl.DataFrame) and not result.is_empty():
                    # Ensure consistent data types for numeric columns
                    df, result = self._ensure_consistent_numeric_types(df, result)
                    df = pl.concat([df, result])

            # Process retrieved data if DataFrame is not empty
            if not df.is_empty():
                # Ensure metadata is available for processing
                df = self.__get_cleaned_table(
                    df=df,
                    alias=alias,
                    cal=cal,
                    device_id=device_id,
                    sensor_list=sensor_list,
                    on_prem=on_prem,
                    unix=unix,
                    metadata=metadata,
                )

            return df

        except aiohttp.ClientError as e:
            error_message = f"HTTPException: {e}"
            await self.logger.error(error_message, self.extra_params)
            return pl.DataFrame()

        except (TypeError, ValueError) as e:
            error_message = f"Type Error: {type(e).__name__}: {e}"
            await self.logger.error(error_message, self.extra_params)
            return pl.DataFrame()

        except Exception as e:
            error_message = f"Unexpected Exception: {e}"
            await self.logger.critical(error_message, self.extra_params)
            return pl.DataFrame()

    async def _fetch_sensor_data(
        self,
        url: str,
        device_id: str,
        sensor: str,
        end_time: int,
        n: int,
    ) -> pl.DataFrame:
        """
        Fetch data for a single sensor with retry logic and cursor-based pagination.

        Args:
            url: API endpoint URL
            device_id: Device identifier
            sensor: Sensor identifier
            end_time: End time in Unix timestamp (milliseconds)
            n: Number of data points to retrieve

        Returns:
            pl.DataFrame: DataFrame containing sensor data or empty DataFrame on error
        """
        df = pl.DataFrame()
        cursor = {"end": end_time, "limit": n}
        retry = 0

        while cursor["end"]:
            session = None
            try:
                params = {
                    "device": device_id,
                    "sensor": sensor,
                    "eTime": cursor["end"],
                    "lim": cursor["limit"],
                    "cursor": "true",
                }

                # Get shared connector and ensure it's healthy
                connector = await self._get_shared_connector()

                session = aiohttp.ClientSession(
                    timeout=self.timeout,
                    headers=self.headers,
                    connector=connector,
                    connector_owner=False,  # Don't close the shared connector when session closes
                )

                async with session.get(url, params=params, ssl=False) as response:
                    response.raise_for_status()
                    response_content = await response.json()

                # Check for errors in the API response
                if "success" in response_content:
                    raise aiohttp.ClientError("API response indicates failure")

                data = response_content["data"]
                if data:
                    batch_df = pl.DataFrame(data, schema_overrides={"value": pl.Float64}, strict=False)
                    # Ensure consistent data types for numeric columns
                    df, batch_df = self._ensure_consistent_numeric_types(df, batch_df)
                    df = pl.concat([df, batch_df])

                cursor = response_content.get("cursor", {"end": None})

            except Exception as e:
                retry += 1

                if retry < c.MAX_RETRIES:
                    sleep_time = c.RETRY_DELAY[1] if retry > 5 else c.RETRY_DELAY[0]
                    await asyncio.sleep(sleep_time)
                else:
                    error_message = f"[URL] {url} - [EXCEPTION] {e}"
                    await self.logger.error(
                        f"Max retries exceeded for sensor {sensor}: {error_message}",
                        self.extra_params,
                    )
                    break
            finally:
                # Always close the session to prevent resource leaks
                if session and not session.closed:
                    await session.close()

        return df

    async def get_firstdp(
        self,
        device_id: str,
        sensor_list: Optional[List] = None,
        cal: Optional[bool] = True,
        start_time: Union[str, int, datetime] = None,
        n: Optional[int] = 1,
        alias: Optional[bool] = False,
        unix: Optional[bool] = False,
        on_prem: Optional[bool] = None,
    ) -> pl.DataFrame:
        """
        Fetches the first data point after a specified start time for a given device and sensor list asynchronously.

        Parameters:
        - start_time (Union[str, int, datetime]): The start time for the query (can be a string, integer, or datetime).
        - device_id (str): The ID of the device.
        - sensor_list (Optional[List]): List of sensor IDs to query data for. Defaults to all sensors if not provided.
        - n (Optional[int]): Number of data points to retrieve. Defaults to 1.
        - cal (bool): Flag indicating whether to perform calibration on the data. Defaults to True.
        - alias (bool): Flag indicating whether to use sensor aliases in the DataFrame. Defaults to False.
        - unix (bool): Flag indicating whether to return timestamps as Unix timestamps. Defaults to False.
        - on_prem (Optional[bool]): Indicates if the operation is on-premise. Defaults to class attribute if not provided.

        Returns:
        - pl.DataFrame: The DataFrame containing the retrieved data points.

        Example:
            >>> data_access = AsyncDataAccess(user_id="my_user_id", data_url="data.url.com", ds_url="example_ds.com")
            >>> df = await data_access.get_firstdp(device_id="XYZ",sensor_list= ['X'],alias=True,cal=True,start_time=1685767732710,unix=False)
            >>> print(df)

        Exceptions Handled:
        - TypeError: Raised when there is a type mismatch in the input parameters.
        - aiohttp.ClientError: Raised when there is an issue with the HTTP request.
        - Exception: General exception handling for other errors.
        """
        try:
            metadata = None
            # Validate input parameters
            if n < 1:
                raise ValueError("Parameter 'n' must be greater than or equal to 1")

            df_devices = await self.get_device_details(on_prem=on_prem)

            # Check if the device is added in the account
            if device_id not in df_devices["devID"].to_list():
                raise Exception(f"Message: Device {device_id} not added in account")

            need_metadata = sensor_list is None or cal or alias
            if need_metadata:
                # Fetch metadata if sensor_list is not provided
                metadata = await self.get_device_metadata(device_id, on_prem)

                if sensor_list is None:
                    sensor_list = list(map(itemgetter("sensorId"), metadata["sensors"]))

                # Ensure sensor_list is not empty
                if not sensor_list:
                    raise Exception("No sensor data available.")

            # Convert start_time to Unix timestamp
            start_time = self.time_to_unix(start_time)

            # If on_prem is not provided, use the default value from the class attribute
            if on_prem is None:
                on_prem = self.on_prem
            protocol = "http" if on_prem else "https"

            # Construct API URL for data retrieval (using GET_FIRST_DP endpoint)
            url = c.GET_FIRST_DP.format(protocol=protocol, data_url=self.data_url)

            # Prepare parameters - different from get_dp, this is a single request
            sensor_values = ",".join(sensor_list)
            params = {
                "device": device_id,
                "sensor": sensor_values,
                "time": start_time // 1000,  # Convert to seconds for this API
            }

            session = None
            async with self.logger.timer("Get First DP Query:", self.extra_params):
                try:
                    # Use shared connector with proper session management
                    connector = await self._get_shared_connector()

                    session = aiohttp.ClientSession(
                        connector=connector,
                        timeout=self.timeout,
                        headers=self.headers,
                        connector_owner=False,  # Don't close the shared connector
                    )

                    async with session.get(url, params=params, ssl=False) as response:
                        response.raise_for_status()
                        response_content = await response.json()

                    # Check for errors in the API response
                    if "success" in response_content:
                        raise aiohttp.ClientError("API response indicates failure")

                    # Process the response data (first element, different from get_dp)
                    data = response_content[0]
                    # Initialize formatted data list
                    formatted_data = []

                    # Process the nested data structure
                    for sensor_data in data.values():
                        if isinstance(sensor_data, dict):
                            pass
                        else:
                            if not sensor_data:
                                continue
                            sensor_data = sensor_data[0]

                        formatted_data.append(
                            {
                                "time": sensor_data.get("time", ""),
                                "sensor": sensor_data.get("sensor", ""),
                                "value": sensor_data.get("value", None),
                            }
                        )

                    # Create DataFrame from formatted data
                    df = (
                        pl.DataFrame(formatted_data, schema_overrides={"value": pl.Float64}, strict=False)
                        if formatted_data
                        else pl.DataFrame()
                    )

                finally:
                    # Always close the session to prevent resource leaks
                    if session and not session.closed:
                        await session.close()

            # Process retrieved data if DataFrame is not empty
            if not df.is_empty():
                # Ensure metadata is available for processing

                df = self.__get_cleaned_table(
                    df=df,
                    alias=alias,
                    cal=cal,
                    device_id=device_id,
                    sensor_list=sensor_list,
                    on_prem=on_prem,
                    unix=unix,
                    metadata=metadata,
                )

            return df

        except aiohttp.ClientError as e:
            error_message = f"HTTPException: {e}"
            await self.logger.error(error_message, self.extra_params)
            return pl.DataFrame()

        except (TypeError, ValueError) as e:
            error_message = f"Type Error: {type(e).__name__}: {e}"
            await self.logger.error(error_message, self.extra_params)
            return pl.DataFrame()

        except Exception as e:
            error_message = f"Unexpected Exception: {e}"
            import traceback

            traceback.print_exc()
            await self.logger.critical(error_message, self.extra_params)
            return pl.DataFrame()

    async def data_query(
        self,
        device_id: str,
        sensor_list: Optional[List] = None,
        start_time: Union[str, int, datetime] = None,
        end_time: Optional[Union[str, int, datetime]] = None,
        cal: Optional[bool] = True,
        alias: Optional[bool] = False,
        unix: Optional[bool] = False,
        on_prem: Optional[bool] = None,
    ) -> pl.DataFrame:
        """
        Queries and retrieves sensor data for a given device within a specified time range asynchronously.

        Parameters:
        - device_id (str): The ID of the device.
        - start_time (Union[str, int, datetime]): The start time for the query (can be a string, integer, or datetime).
        - end_time (Optional[Union[str, int, datetime]]): The end time for the query (can be a string, integer, or datetime). Defaults to None.
        - sensor_list (Optional[List]): List of sensor IDs to query data for. Defaults to all sensors if not provided.
        - cal (bool): Flag indicating whether to perform calibration on the data. Defaults to True.
        - alias (bool): Flag indicating whether to use sensor aliases in the DataFrame. Defaults to False.
        - unix (bool): Flag indicating whether to return timestamps as Unix timestamps. Defaults to False.
        - on_prem (Optional[bool]): Indicates if the operation is on-premise. Defaults to class attribute if not provided.
        - metadata : Optional[dict], default=None
            Additional metadata related to sensors or calibration parameters.

        Returns:
        - pl.DataFrame: The DataFrame containing the queried sensor data.

        Example:
            >>> data_access = AsyncDataAccess(user_id="my_user_id", data_url="data.url.com", ds_url="example_ds.com")
            >>> df = await data_access.data_query("XYZ",sensor_list = ["X","Y"],end_time=1717419975210,start_time=1685767732000,alias=True)
            >>> print(df)

        Exceptions Handled:
        - TypeError: Raised when there is a type mismatch in the input parameters.
        - aiohttp.ClientError: Raised when there is an issue with the HTTP request.
        - Exception: General exception handling for other errors.
        """
        try:
            metadata = None

            df_devices = await self.get_device_details(on_prem=on_prem)

            # Check if the device is added in the account
            if device_id not in df_devices["devID"].to_list():
                raise Exception(f"Message: Device {device_id} not added in account")

            # Fetch metadata if sensor_list is not provided
            need_metadata = sensor_list is None or cal or alias
            if need_metadata:
                # Fetch metadata if sensor_list is not provided
                metadata = await self.get_device_metadata(device_id, on_prem)

                if sensor_list is None:
                    sensor_list = list(map(itemgetter("sensorId"), metadata["sensors"]))

                # Ensure sensor_list is not empty
                if not sensor_list:
                    raise Exception("No sensor data available.")

            # Resolve on_prem to a boolean value
            if on_prem is None:
                on_prem = self.on_prem

            # Convert timestamps
            start_time_unix = self.time_to_unix(start_time)
            end_time_unix = self.time_to_unix(end_time)

            # Validate that the start time is before the end time
            if end_time_unix < start_time_unix:
                raise ValueError(
                    f"Invalid time range: start_time({start_time}) should be before end_time({end_time})."
                )

            # Use influxdb method for data retrieval
            df = await self.__influxdb(
                device_id=device_id,
                sensor_list=sensor_list,
                start_time=start_time_unix,
                end_time=end_time_unix,
                on_prem=on_prem,
            )

            # Process retrieved data if DataFrame is not empty
            if not df.is_empty():
                df = self.__get_cleaned_table(
                    df=df,
                    alias=alias,
                    cal=cal,
                    device_id=device_id,
                    sensor_list=sensor_list,
                    on_prem=on_prem,
                    unix=unix,
                    metadata=metadata,
                )

            return df

        except aiohttp.ClientError as e:
            error_message = f"HTTPException: {e}"
            await self.logger.error(error_message, self.extra_params)
            return pl.DataFrame()

        except (TypeError, ValueError) as e:
            error_message = f"Type Error: {type(e).__name__}: {e}"
            await self.logger.error(error_message, self.extra_params)
            return pl.DataFrame()

        except Exception as e:
            error_message = f"Unexpected Exception: {e}"
            await self.logger.critical(error_message, self.extra_params)
            return pl.DataFrame()

    async def __influxdb(
        self,
        device_id: str,
        sensor_list: List,
        start_time: int,
        end_time: int,
        on_prem: Optional[bool] = None,
    ) -> pl.DataFrame:
        """
        Private method to query InfluxDB for sensor data asynchronously using cursor-based pagination.

        This method fetches sensor data from the InfluxDB API with cursor-based pagination to handle
        large datasets efficiently. It implements retry logic with exponential backoff for robust
        data retrieval.

        Args:
            device_id (str): The ID of the device to query data for.
            sensor_list (List): List of sensor IDs to retrieve data from.
            start_time (int): The start time in Unix timestamp format (milliseconds).
            end_time (int): The end time in Unix timestamp format (milliseconds).
            on_prem (Optional[bool]): Whether to use on-premises server. If None, uses class default.

        Returns:
            pl.DataFrame: DataFrame containing the retrieved sensor data with columns 'time', 'sensor', and 'value'.

        Notes:
        -----
        - Uses cursor-based pagination to fetch data in batches defined by c.CURSOR_LIMIT
        - Implements retry logic with exponential backoff (c.RETRY_DELAY) up to c.MAX_RETRIES
        - Continues fetching data while cursor["start"] and cursor["end"] are available
        - Returns empty DataFrame if no data is found or if all retries are exhausted
        """
        try:
            # If on_prem is not provided, use the default value from the class attribute
            if on_prem is None:
                on_prem = self.on_prem
            protocol = "http" if on_prem else "https"

            url = c.INFLUXDB_URL.format(protocol=protocol, data_url=self.data_url)

            # Initialize cursor for data retrieval
            cursor = {"start": start_time, "end": end_time}

            sensor_values = ",".join(sensor_list)
            df = pl.DataFrame()
            retry = 0

            async with self.logger.timer("InfluxDB Query:", self.extra_params):
                while cursor["start"] and cursor["end"]:
                    session = None
                    try:
                        # Set the request parameters using cursor values
                        params = {
                            "device": device_id,
                            "sensor": sensor_values,
                            "sTime": cursor["start"],
                            "eTime": cursor["end"],
                            "cursor": "true",
                            "limit": c.CURSOR_LIMIT,
                        }

                        # Get shared connector and ensure it's healthy
                        connector = await self._get_shared_connector()

                        session = aiohttp.ClientSession(
                            timeout=self.timeout,
                            headers=self.headers,
                            connector=connector,
                            connector_owner=False,  # Don't close the shared connector when session closes
                        )

                        async with session.get(
                            url, params=params, ssl=False
                        ) as response:
                            response.raise_for_status()
                            response_content = await response.json()

                        # Check for errors in the API response
                        if "success" in response_content:
                            raise aiohttp.ClientError("API response indicates failure")

                        data = response_content["data"]
                        cursor = response_content["cursor"]

                        # Combine all results, filtering out exceptions
                        if data:
                            batch_df = pl.DataFrame(data, schema_overrides={"value": pl.Float64}, strict=False)
                            # Ensure consistent data types for numeric columns
                            df, batch_df = self._ensure_consistent_numeric_types(df, batch_df)
                            df = pl.concat([df, batch_df])

                    except Exception as e:
                        retry += 1
                        error_message = f"\n[URL] {url}\n[EXCEPTION] {e}"

                        await self.logger.error(
                            f"[{type(e).__name__}] Retry Count: {retry}, {e}"
                            + error_message,
                            self.extra_params,
                        )

                        # Retry with exponential backoff
                        if retry < c.MAX_RETRIES:
                            sleep_time = (
                                c.RETRY_DELAY[1] if retry > 5 else c.RETRY_DELAY[0]
                            )
                            await asyncio.sleep(sleep_time)
                        else:
                            error_message = f"Max retries for data fetching from api-layer exceeded: {error_message}"
                            await self.logger.error(error_message, self.extra_params)
                            break

                    finally:
                        # Always close the session to prevent resource leaks
                        if session and not session.closed:
                            await session.close()

            return df

        except aiohttp.ClientError as e:
            error_message = f"HTTPException: {e}"
            await self.logger.error(error_message, self.extra_params)
            return pl.DataFrame()

        except (TypeError, ValueError) as e:
            error_message = f"Type Error: {type(e).__name__}: {e}"
            await self.logger.error(error_message, self.extra_params)
            return pl.DataFrame()

        except Exception as e:
            error_message = f"Unexpected Exception: {e}"
            await self.logger.critical(error_message, self.extra_params)
            return pl.DataFrame()

    async def _fetch_sensor_time_range_data(
        self,
        url: str,
        device_id: str,
        sensor: str,
        start_time: int,
        end_time: int,
    ) -> pl.DataFrame:
        """
        Fetch time-range data for a single sensor with retry logic and cursor-based pagination.

        Args:
            url: API endpoint URL
            device_id: Device identifier
            sensor: Sensor identifier
            start_time: Start time in Unix timestamp (milliseconds)
            end_time: End time in Unix timestamp (milliseconds)

        Returns:
            pl.DataFrame: DataFrame containing sensor data or empty DataFrame on error
        """
        df = pl.DataFrame()
        retry = 0
        cursor = {"start": start_time, "end": end_time}

        while cursor["start"] and cursor["end"]:
            session = None
            try:
                params = {
                    "device": device_id,
                    "sensor": sensor,
                    "sTime": cursor["start"],
                    "eTime": cursor["end"],
                    "cursor": "true",
                    "limit": c.CURSOR_LIMIT,
                }

                # Get shared connector and ensure it's healthy
                connector = await self._get_shared_connector()

                session = aiohttp.ClientSession(
                    timeout=self.timeout,
                    headers=self.headers,
                    connector=connector,
                    connector_owner=False,  # Don't close the shared connector when session closes
                )

                async with session.get(url, params=params, ssl=False) as response:
                    response.raise_for_status()
                    response_content = await response.json()

                # Check for errors in the API response
                if "success" in response_content:
                    raise aiohttp.ClientError("API response indicates failure")

                data = response_content["data"]
                if data:
                    batch_df = pl.DataFrame(data, schema_overrides={"value": pl.Float64}, strict=False)
                    # Ensure consistent data types for numeric columns
                    df, batch_df = self._ensure_consistent_numeric_types(df, batch_df)
                    df = pl.concat([df, batch_df])

                cursor = response_content.get("cursor", {"start": None, "end": None})

            except Exception as e:
                retry += 1

                if retry < c.MAX_RETRIES:
                    sleep_time = c.RETRY_DELAY[1] if retry > 5 else c.RETRY_DELAY[0]
                    await asyncio.sleep(sleep_time)
                else:
                    error_message = f"[URL] {url} - [EXCEPTION] {e}"
                    await self.logger.error(
                        f"Max retries exceeded for sensor {sensor}: {error_message}",
                        self.extra_params,
                    )
                    break
            finally:
                # Always close the session to prevent resource leaks
                if session and not session.closed:
                    await session.close()

        return df

    async def data_query_parallel(
        self,
        device_id: str,
        sensor_list: Optional[List] = None,
        start_time: Union[str, int, datetime] = None,
        end_time: Optional[Union[str, int, datetime]] = None,
        cal: Optional[bool] = True,
        alias: Optional[bool] = False,
        unix: Optional[bool] = False,
        on_prem: Optional[bool] = None,
    ) -> pl.DataFrame:
        """
        Queries and retrieves sensor data for a given device within a specified time range using parallel sensor requests.

        This method is similar to data_query but makes parallel requests for each sensor instead of using
        a single bulk InfluxDB query. This can be more efficient for certain scenarios, especially when
        dealing with a small number of sensors or when the InfluxDB endpoint has limitations.

        Parameters:
        - device_id (str): The ID of the device.
        - start_time (Union[str, int, datetime]): The start time for the query.
        - end_time (Optional[Union[str, int, datetime]]): The end time for the query.
        - sensor_list (Optional[List]): List of sensor IDs to query data for. Defaults to all sensors if not provided.
        - cal (bool): Flag indicating whether to perform calibration on the data. Defaults to True.
        - alias (bool): Flag indicating whether to use sensor aliases in the DataFrame. Defaults to False.
        - unix (bool): Flag indicating whether to return timestamps as Unix timestamps. Defaults to False.
        - on_prem (Optional[bool]): Indicates if the operation is on-premise. Defaults to class attribute if not provided.

        Returns:
        - pl.DataFrame: The DataFrame containing the queried sensor data.

        Example:
            >>> data_access = AsyncDataAccess(user_id="my_user_id", data_url="data.url.com", ds_url="example_ds.com")
            >>> df = await data_access.data_query_parallel("XYZ", sensor_list=["X","Y"], end_time=1717419975210, start_time=1685767732000, alias=True)
            >>> print(df)
        """
        try:
            metadata = None

            df_devices = await self.get_device_details(on_prem=on_prem)

            # Check if the device is added in the account
            if device_id not in df_devices["devID"].to_list():
                raise Exception(f"Message: Device {device_id} not added in account")

            need_metadata = sensor_list is None or cal or alias
            if need_metadata:
                # Fetch metadata if sensor_list is not provided
                metadata = await self.get_device_metadata(device_id, on_prem)

                if sensor_list is None:
                    sensor_list = list(map(itemgetter("sensorId"), metadata["sensors"]))

                # Ensure sensor_list is not empty
                if not sensor_list:
                    raise Exception("No sensor data available.")

            # Resolve on_prem to a boolean value
            if on_prem is None:
                on_prem = self.on_prem

            # Convert timestamps
            start_time_unix = self.time_to_unix(start_time)
            end_time_unix = self.time_to_unix(end_time)

            # Validate that the start time is before the end time
            if end_time_unix < start_time_unix:
                raise ValueError(
                    f"Invalid time range: start_time({start_time}) should be before end_time({end_time})."
                )

            protocol = "http" if on_prem else "https"
            url = c.INFLUXDB_URL.format(protocol=protocol, data_url=self.data_url)

            # Process all sensors concurrently for better performance
            sensor_tasks = [
                self._fetch_sensor_time_range_data(
                    url, device_id, sensor, start_time_unix, end_time_unix
                )
                for sensor in sensor_list
            ]

            async with self.logger.timer("Parallel Data Query:", self.extra_params):
                # Execute all sensor data fetches concurrently
                sensor_results = await asyncio.gather(
                    *sensor_tasks, return_exceptions=True
                )

            # Combine all results, filtering out exceptions
            df = pl.DataFrame()
            for result in sensor_results:
                if isinstance(result, pl.DataFrame) and not result.is_empty():
                    # Ensure consistent data types for numeric columns
                    df, result = self._ensure_consistent_numeric_types(df, result)
                    df = pl.concat([df, result])

            # Process retrieved data if DataFrame is not empty
            if not df.is_empty():
                # Ensure metadata is available for processing

                df = self.__get_cleaned_table(
                    df=df,
                    alias=alias,
                    cal=cal,
                    device_id=device_id,
                    sensor_list=sensor_list,
                    on_prem=on_prem,
                    unix=unix,
                    metadata=metadata,
                )

            return df

        except aiohttp.ClientError as e:
            error_message = f"HTTPException: {e}"
            await self.logger.error(error_message, self.extra_params)
            return pl.DataFrame()

        except (TypeError, ValueError) as e:
            error_message = f"Type Error: {type(e).__name__}: {e}"
            await self.logger.error(error_message, self.extra_params)
            return pl.DataFrame()

        except Exception as e:
            error_message = f"Unexpected Exception: {e}"
            await self.logger.critical(error_message, self.extra_params)
            return pl.DataFrame()

    async def get_load_entities(
        self, on_prem: Optional[bool] = None, clusters: Optional[list] = None
    ) -> list:
        """
        Fetches load entities from an API asynchronously, handling pagination and optional filtering by cluster names.

        Args:
            on_prem (Optional[bool]): Specifies whether to use on-premise settings for the request.
                                      Defaults to None, which uses the class attribute `self.on_prem`.
            clusters (Optional[list]): A list of cluster names to filter the results by.
                                       Defaults to None, which returns all clusters.

        Returns:
            list: A list of load entities. If clusters are provided, only entities belonging to the specified clusters are returned.

        Raises:
            Exception: If no clusters are provided or if the maximum retry limit is reached.
            TypeError, ValueError, aiohttp.ClientError: For other request-related exceptions.

        Example:
            >>> data_access = AsyncDataAccess(user_id="my_user_id", data_url="data.url.com", ds_url="example_ds.com")

            >>> # Fetch all load entities using on-premise settings
            >>> all_entities = await data_access.get_load_entities()

            >>> # Fetch load entities and filter by specific cluster names
            >>> specific_clusters = await data_access.get_load_entities(clusters=["cluster1", "cluster2"])

            >>> # Fetch load entities using on-premise settings, but no specific clusters
            >>> on_prem_entities = await data_access.get_load_entities(on_prem=True)

        """
        try:
            # Validate clusters input
            if clusters is not None and len(clusters) == 0:
                raise Exception("No clusters provided.")

            # If on_prem is not provided, use the default value from the class attribute
            if on_prem is None:
                on_prem = self.on_prem
            protocol = "http" if on_prem else "https"

            page_count = 1
            cluster_count = None
            retry = 0

            result = []

            # Construct API URL for data retrieval
            url = c.GET_LOAD_ENTITIES.format(
                protocol=protocol,
                data_url=self.data_url,
            )

            async with self.logger.timer("Get Load Entities Query:", self.extra_params):
                while True:
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

                        async with session.get(
                            url + f"/{self.user_id}/{page_count}/{cluster_count}",
                            ssl=False,
                        ) as response:
                            response.raise_for_status()
                            response_data = await response.json()

                        if "error" in response_data:
                            await self.logger.error(
                                f"API Error: {response_data}", self.extra_params
                            )
                            return []

                        # Extend result with retrieved response_data
                        result.extend(response_data["data"])

                        total_count = response_data["totalCount"]
                        clusters_recieved = len(result)

                        # Break the loop if all clusters have been received
                        if clusters_recieved == total_count:
                            break

                        # Update for next page
                        page_count += 1
                        cluster_count = total_count - clusters_recieved

                    except Exception as e:
                        retry += 1

                        if retry < c.MAX_RETRIES:
                            sleep_time = (
                                c.RETRY_DELAY[1] if retry > 5 else c.RETRY_DELAY[0]
                            )
                            await asyncio.sleep(sleep_time)
                        else:
                            error_message = f"[URL] {url} [EXCEPTION] {e}"
                            await self.logger.error(
                                f"Max retries for data fetching from api-layer exceeded: {error_message}",
                                self.extra_params,
                            )
                            break
                    finally:
                        # Always close the session to prevent resource leaks
                        if session and not session.closed:
                            await session.close()
            # Filter results by cluster names if provided
            if clusters is not None:
                return [item for item in result if item["name"] in clusters]

            return result

        except aiohttp.ClientError as e:
            error_message = f"HTTPException: {e}"
            await self.logger.error(error_message, self.extra_params)
            return []

        except (TypeError, ValueError) as e:
            error_message = f"Type Error: {type(e).__name__}: {e}"
            await self.logger.error(error_message, self.extra_params)
            return []

        except Exception as e:
            error_message = f"Unexpected Exception: {e}"
            await self.logger.critical(error_message, self.extra_params)
            return []

    async def consumption(
        self,
        device_id: str,
        sensor: str,
        interval: Optional[int] = None,
        start_time: Union[str, int, datetime] = None,
        end_time: Optional[Union[str, int, datetime]] = None,
        cal: Optional[bool] = True,
        alias: Optional[bool] = False,
        unix: Optional[bool] = False,
        on_prem: Optional[bool] = None,
    ) -> pl.DataFrame:
        """
        Fetch consumption data for a specified device and sensor within a given time range asynchronously.

        This method retrieves consumption data for a device's sensor, applies optional calibration
        and alias adjustments, handles time conversion (Unix or datetime), and supports custom intervals
        for data aggregation. Data is retrieved via an API call, with a retry mechanism to handle potential failures.

        Args:
        - device_id (str): The unique identifier for the device.
        - sensor (str): The name of the sensor for which data is to be retrieved.
        - interval (int, optional): Custom time interval (in seconds) for data aggregation.
          If None, automatically sets disable_interval=True for optimal performance. Defaults to None.
        - start_time (Union[str, int, datetime], optional): The start time of the data retrieval period.
          Can be provided as a string, integer timestamp, or datetime object.
        - end_time (Union[str, int, datetime], optional): The end time of the data retrieval period.
          Can be provided as a string, integer timestamp, or datetime object.
        - cal (bool, optional): If True, applies calibration adjustments to the sensor data. Defaults to True.
        - alias (bool, optional): If True, applies sensor alias mapping. Defaults to False.
        - unix (bool, optional): If True, output times are in Unix milliseconds. Defaults to False (returns datetime).
        - on_prem (bool, optional): Overrides on-premises data access. If None, uses the default instance attribute.
          Defaults to None.
        - disable_interval (bool, optional): Disables custom interval and uses the default data frequency.
          Automatically set to True if interval is None. Defaults to False.

        Returns:
        - pl.DataFrame: A DataFrame containing the time and sensor values within the specified time range.

        Raises:
        - ValueError: If the provided `start_time` is later than the `end_time`.
        - Exception: If the device is not found in the user's account or if maximum retries for data fetching are exceeded.
        - aiohttp.ClientError: For issues with the HTTP request to fetch the data.

        Example:
            >>> data_access = AsyncDataAccess(user_id="my_user_id", data_url="data.url.com", ds_url="example_ds.com")
            >>> df = await data_access.consumption("XYZ", sensor="D99", end_time=1720308782000, start_time=1719790382000, alias=True, cal=True, unix=False)

        Notes:
        - A retry mechanism is implemented with exponential backoff. If data fetching fails after
          exceeding the maximum number of retries (`c.MAX_RETRIES`), an exception is raised.
        - Timestamps are internally converted to Unix milliseconds for API compatibility unless
          `unix=False`, in which case timestamps are converted back to datetime with the appropriate timezone.
        - If the `cal` flag is set, calibration data is applied based on the device and sensor metadata.
        - The `alias` flag allows applying a sensor alias mapping to the data, based on predefined sensor aliases.
        - Smart optimization: When `interval=None`, `disable_interval` is automatically set to `True`
          for optimal API performance, as no custom interval aggregation is needed.
        """
        try:
            metadata = None
            time_stamp = {}
            disable_interval = True

            # Convert start_time and end_time to Unix timestamps
            time_stamp["startTime"] = self.time_to_unix(start_time)
            time_stamp["endTime"] = self.time_to_unix(end_time)

            # Validate that the start time is before the end time
            if time_stamp["endTime"] < time_stamp["startTime"]:
                raise ValueError(
                    f"Invalid time range: start_time({start_time}) should be before end_time({end_time})."
                )

            # If on_prem is not provided, use the default value from the class attribute
            if on_prem is None:
                on_prem = self.on_prem

            protocol = "http" if on_prem else "https"

            # Fetch device details to verify if the device exists in the account
            df_devices = await self.get_device_details(on_prem=on_prem)

            # Check if the device is added in the account
            if device_id not in df_devices["devID"].to_list():
                raise Exception(f"Message: Device {device_id} not added in account")

            # Construct API URL for data retrieval
            url = c.CONSUMPTION_URL.format(protocol=protocol, data_url=self.data_url)

            retry = 0

            # Smart optimization: if interval is None, automatically disable threshold
            if interval is not None:
                disable_interval = False

            payload = {
                "device": device_id,
                "sensor": sensor,
                "startTime": time_stamp["startTime"],
                "endTime": time_stamp["endTime"],
                "disableThreshold": str(disable_interval).lower(),
            }

            # Only add custom interval if it's provided and threshold is not disabled
            if interval is not None:
                payload["customIntervalInSec"] = interval

            session = None
            response_data = None

            async with self.logger.timer("Consumption Query:", self.extra_params):
                # Retry mechanism for fetching data from API
                while True:
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
                            url, params=payload, ssl=False
                        ) as response:
                            response.raise_for_status()
                            response_data = await response.json()

                        if "errors" in response_data:
                            raise aiohttp.ClientError("API response contains errors")

                        break

                    except Exception as e:
                        retry += 1

                        if retry < c.MAX_RETRIES:
                            sleep_time = (
                                c.RETRY_DELAY[1] if retry > 5 else c.RETRY_DELAY[0]
                            )
                            await asyncio.sleep(sleep_time)
                        else:
                            error_message = f"[URL] {url} - [EXCEPTION] {e}"

                            await self.logger.error(
                                f"Max retries for data fetching from api-layer exceeded: {error_message}",
                                self.extra_params,
                            )
                            return pl.DataFrame()

                    finally:
                        # Always close the session to prevent resource leaks
                        if session and not session.closed:
                            await session.close()
                        session = None

            # Initialize lists to store time and sensor values
            time_list = []
            sensor_list = []

            # Iterate through the dictionary to populate the lists
            for key, value in response_data.items():
                if isinstance(value, dict):
                    time_list.append(value.get("time", time_stamp[key]))
                    sensor_list.append(value.get("value", None))
                else:
                    time_list.append(time_stamp[key])
                    sensor_list.append(None)

            # Create the DataFrame
            df = pl.DataFrame({"time": time_list, sensor: sensor_list}, strict=False)

            # Process the DataFrame if it's not empty
            if not df.is_empty():
                # Ensure time column is in datetime format
                df = df.with_columns(
                    [
                        pl.col("time")
                        .cast(pl.Int64)
                        .map_elements(
                            lambda x: datetime.fromtimestamp(x / 1000, tz=self.tz),
                            return_dtype=pl.Datetime("us", str(self.tz)),
                        )
                        .alias("time")
                    ]
                )

                # Fetch metadata if calibration or alias is required
                if (cal or alias) and metadata is None:
                    metadata = await self.get_device_metadata(device_id, on_prem)

                df = self.__get_cleaned_table(
                    df=df,
                    alias=alias,
                    cal=cal,
                    device_id=device_id,
                    sensor_list=[sensor],
                    on_prem=on_prem,
                    unix=unix,
                    metadata=metadata,
                    pivot_table=False,
                )

            return df

        except aiohttp.ClientError as e:
            error_message = f"HTTPException: {e}"
            await self.logger.error(error_message, self.extra_params)
            return pl.DataFrame()

        except (TypeError, ValueError) as e:
            error_message = f"Type Error: {type(e).__name__}: {e}"
            await self.logger.error(error_message, self.extra_params)
            return pl.DataFrame()

        except Exception as e:
            error_message = f"Unexpected Exception: {e}"
            await self.logger.critical(error_message, self.extra_params)
            return pl.DataFrame()

    async def trigger_paramter(
        self, title_list: list, on_prem: Optional[bool] = None
    ) -> list:
        """
        Triggers a parameter-based operation on the server by sending a list of titles asynchronously.

        This method sends a request to the API with the provided list of titles, triggering
        a server-side operation. The method retries in case of failure, up to a maximum retry limit.

        Args:
            title_list (list): A list of titles to be used for triggering the operation.
            on_prem (bool, optional): Whether the operation is performed on-premises.
                If not provided, the class attribute value is used.

        Returns:
            list: The data returned from the server after triggering the operation, or an empty list in case of an error.

        Raises:
            Exception: If the maximum retries for data fetching are exceeded.
            ValueError: If there is an issue with the input values.

        Example usage:

        ```python
        data_access = AsyncDataAccess(user_id="my_user_id", data_url="data.url.com", ds_url="example_ds.com")

        # Example: Trigger a parameter operation with a list of titles
        result = await data_access.trigger_paramter(
            title_list=["Title1", "Title2", "Title3"]
        )
        ```
        """
        try:
            # If on_prem is not provided, use the default value from the class attribute
            if on_prem is None:
                on_prem = self.on_prem
            protocol = "http" if on_prem else "https"

            # Construct API URL for data retrieval
            url = c.TRIGGER_URL.format(
                protocol=protocol,
                data_url=self.data_url,
            )
            retry = 0

            headers = {"Content-Type": "application/json"}

            payload = {"userID": self.user_id, "title": title_list}
            session = None

            async with self.logger.timer("Trigger Parameter Query:", self.extra_params):
                while True:
                    try:
                        # Use shared connector with proper session management
                        connector = await self._get_shared_connector()

                        session = aiohttp.ClientSession(
                            connector=connector,
                            timeout=self.timeout,
                            headers=self.headers,
                            connector_owner=False,  # Don't close the shared connector
                        )

                        async with session.put(
                            url, json=payload, headers=headers, ssl=False
                        ) as response:
                            response.raise_for_status()
                            response_data = await response.json()

                        if "error" in response_data:
                            raise ValueError("API response contains error")

                        return response_data.get("data", [])

                    except Exception as e:
                        retry += 1
                        error_message = f"[URL] {url} - [EXCEPTION] {e}"

                        if retry < c.MAX_RETRIES:
                            sleep_time = (
                                c.RETRY_DELAY[1] if retry > 5 else c.RETRY_DELAY[0]
                            )
                            await asyncio.sleep(sleep_time)
                        else:
                            await self.logger.error(
                                f"Max retries for data fetching from api-layer exceeded: {error_message}",
                                self.extra_params,
                            )
                            return []

                    finally:
                        # Always close the session to prevent resource leaks
                        if session and not session.closed:
                            await session.close()

        except aiohttp.ClientError as e:
            error_message = f"HTTPException: {e}"
            await self.logger.error(error_message, self.extra_params)
            return []

        except (TypeError, ValueError) as e:
            error_message = f"Type Error: {type(e).__name__}: {e}"
            await self.logger.error(error_message, self.extra_params)
            return []

        except Exception as e:
            error_message = f"Unexpected Exception: {e}"
            await self.logger.critical(error_message, self.extra_params)
            return []

    async def get_filtered_operation_data(
        self,
        device_id: str,
        sensor_list: Optional[list] = None,
        operation: Optional[Literal["min", "max", "last", "first"]] = None,
        filter_operator: Optional[
            Literal[">", "<", "<=", ">=", "!=", "==", "><", "<>"]
        ] = None,
        threshold: Optional[str] = None,
        start_time: Union[str, int, datetime] = None,
        end_time: Optional[Union[str, int, datetime]] = None,
        df: Optional[pl.DataFrame] = None,
        cal: Optional[bool] = True,
        alias: Optional[bool] = False,
        unix: Optional[bool] = False,
        on_prem: Optional[bool] = None,
    ) -> pl.DataFrame:
        """
        Retrieves filtered operation data for a specific device over a specified time range asynchronously.

        This method fetches sensor data by communicating with a data API, applying various
        operations like min, max, first, last, or filter operators with thresholds, and returns
        the data in a cleaned DataFrame format.

        Args:
            device_id (str): The ID of the device for which data is to be fetched.
            sensor_list (list, optional): List of sensors to retrieve data from. Defaults to None.
            operation (Literal["min", "max", "last", "first"], optional): Operation to apply to the data.
            filter_operator (Literal[">", "<", "<=", ">=", "!=", "==", "><", "<>"], optional): Filter operator.
            threshold (str, optional): Threshold value for filtering sensor data.
            start_time (Union[str, int, datetime]): The start time for data retrieval.
            end_time (Union[str, int, datetime], optional): The end time for data retrieval.
            df (pl.DataFrame, optional): A DataFrame containing sensor configurations (sensor, operation, filter_operator, threshold).
            cal (bool, optional): Whether to apply calibration to the data. Default is True.
            alias (bool, optional): Whether to return sensor names as aliases. Default is False.
            unix (bool, optional): Whether to return time in Unix format. Default is False.
            on_prem (bool, optional): Whether to fetch data from an on-premises system. If None, uses class-level setting.

        Returns:
            pl.DataFrame: A DataFrame containing the retrieved sensor data, or an empty DataFrame if an error occurs.

        Raises:
            ValueError: If time ranges are invalid, columns in the DataFrame are missing or inconsistent, or if operations or filters are not properly set.
            Exception: If the device is not found in the account, or if the maximum retries for data fetching are exceeded.

        Example usage:

        ```python
        data_access = AsyncDataAccess(user_id="my_user_id", data_url="data.url.com", ds_url="example_ds.com")

        # Example 1: Fetch the minimum value for sensors on device 'device_123' between two timestamps
        df = await data_access.get_filtered_operation_data(
            device_id="device_123",
            sensor_list=["sensor_1", "sensor_2"],
            operation="min",
            start_time="2024-09-01T00:00:00Z",
            end_time="2024-09-10T23:59:59Z"
        )

        # Example 2: Fetch data using a DataFrame with sensors, operations, and filters
        import polars as pl

        sensor_df = pl.DataFrame({
            "sensor": ["sensor_1", "sensor_2"],
            "operation": ["last", "max"],
            "filter_operator": [">", "<"],
            "threshold": ["50", "100"]
        })

        df_filtered = await data_access.get_filtered_operation_data(
            device_id="device_123",
            df=sensor_df,
            start_time=1693771200,  # Unix timestamp
            end_time=1694359200  # Unix timestamp
        )
        ```
        """
        try:
            metadata = None

            # If on_prem is not provided, use the default value from the class attribute
            if on_prem is None:
                on_prem = self.on_prem
            protocol = "http" if on_prem else "https"

            # Convert start_time and end_time to Unix timestamps
            start_time_unix = self.time_to_unix(start_time)
            end_time_unix = self.time_to_unix(end_time)

            # Validate that the start time is before the end time
            if end_time_unix < start_time_unix:
                raise ValueError(
                    f"Invalid time range: start_time({start_time}) should be before end_time({end_time})."
                )

            df_devices = await self.get_device_details(on_prem=on_prem)

            # Check if the device is added in the account
            if device_id not in df_devices["devID"].to_list():
                raise Exception(f"Message: Device {device_id} not added in account")

            # Initialize the request body with userID, startTime, and endTime
            request_body = {
                "userID": self.user_id,
                "startTime": start_time_unix,
                "endTime": end_time_unix,
                "devConfig": [],
            }

            if df is not None:
                # Check if all required columns are present in the DataFrame
                required_columns = {"sensor", "operation"}
                if not required_columns.issubset(df.columns):
                    raise ValueError(
                        f"DataFrame must contain the following columns: {required_columns}"
                    )

                # Check for duplicates in the 'sensor' column
                if df["sensor"].is_duplicated().any():
                    raise ValueError(
                        "Duplicate values detected in the 'sensor' column. Please ensure all sensor entries are unique."
                    )

                # Check if filter_operator and threshold columns are both present or both absent
                if ("filter_operator" in df.columns) != ("threshold" in df.columns):
                    raise ValueError(
                        "Both 'filter_operator' and 'threshold' columns must be present together or not at all."
                    )
                elif ("filter_operator" in df.columns) and ("threshold" in df.columns):
                    # Check for consistent null values
                    filter_not_null = df["filter_operator"].is_not_null()
                    threshold_not_null = df["threshold"].is_not_null()
                    if not (filter_not_null == threshold_not_null).all():
                        raise ValueError(
                            "Inconsistent null values: If 'filter_operator' is present in a row, 'threshold' must also be present in that row, and vice versa."
                        )

                sensor_list = []

                # Iterate through each row in the DataFrame to build the request body
                for row in df.iter_rows(named=True):
                    sensor_list.append(row["sensor"])
                    # Basic sensor configuration with mandatory fields
                    sensor_config = {
                        "devID": device_id,
                        "sensorID": row["sensor"],
                        "operation": row["operation"],
                    }

                    # Conditionally add filter_operator and threshold if they are present and not empty
                    filter_operator_val = row.get("filter_operator", None)
                    threshold_val = row.get("threshold", None)

                    if filter_operator_val is not None and threshold_val is not None:
                        sensor_config["operator"] = filter_operator_val
                        sensor_config["operatorValue"] = threshold_val

                    # Append the sensor configuration to devConfig
                    request_body["devConfig"].append(sensor_config)

            else:
                if operation is None:
                    raise ValueError("The 'operation' variable must be set.")

                # Validate that both filter_operator and threshold are either both present or both absent
                if (filter_operator is None) != (threshold is None):
                    raise ValueError(
                        "Both filter_operator and threshold must be provided together or not at all."
                    )

                # Fetch metadata if sensor_list is not provided
                if sensor_list is None:
                    metadata = await self.get_device_metadata(device_id, on_prem)
                    sensor_list = list(map(itemgetter("sensorId"), metadata["sensors"]))

                # Iterate through the sensor_list to populate devConfig
                for sensor_id in sensor_list:
                    # Create the configuration dictionary for each sensor
                    sensor_config = {
                        "devID": device_id,
                        "sensorID": sensor_id,
                        "operation": operation,
                    }

                    # Add filter_operator and operatorValue only if they are both present
                    if filter_operator is not None and threshold is not None:
                        sensor_config["operator"] = filter_operator
                        sensor_config["operatorValue"] = threshold

                    # Append the configuration to devConfig
                    request_body["devConfig"].append(sensor_config)

            # Construct API URL for data retrieval
            url = c.GET_FILTERED_OPERATION_DATA.format(
                protocol=protocol,
                data_url=self.data_url,
            )

            retry = 0
            session = None
            response_data = None

            async with self.logger.timer(
                "Get Filtered Operation Data Query:", self.extra_params
            ):
                while True:
                    try:
                        # Use shared connector with proper session management
                        connector = await self._get_shared_connector()

                        session = aiohttp.ClientSession(
                            connector=connector,
                            timeout=self.timeout,
                            headers=self.headers,
                            connector_owner=False,  # Don't close the shared connector
                        )

                        async with session.put(
                            url, json=request_body, headers=self.headers, ssl=False
                        ) as response:
                            response.raise_for_status()
                            response_data = await response.json()

                        if "errors" in response_data:
                            raise aiohttp.ClientError("API response contains errors")
                        break

                    except Exception as e:
                        retry += 1

                        if retry < c.MAX_RETRIES:
                            sleep_time = (
                                c.RETRY_DELAY[1] if retry > 5 else c.RETRY_DELAY[0]
                            )
                            await asyncio.sleep(sleep_time)
                        else:
                            error_message = f"[URL] {url} - [EXCEPTION] {e}"
                            await self.logger.error(
                                f"Max retries for data fetching from api-layer exceeded: {error_message}",
                                self.extra_params,
                            )
                            return pl.DataFrame()

                    finally:
                        # Always close the session to prevent resource leaks
                        if session and not session.closed:
                            await session.close()

            retrieved_sensors = []
            time_list = []
            value_list = []

            for sensor in sensor_list:
                if df is not None:
                    # Get operation from the DataFrame for this sensor
                    operation_val = df.filter(pl.col("sensor") == sensor)["operation"][
                        0
                    ]
                else:
                    operation_val = operation

                info = response_data["data"].get(
                    f"{device_id}_{sensor}_{operation_val}"
                )
                if info:
                    retrieved_sensors.append(sensor)
                    time_list.append(info["time"])
                    value_list.append(info["value"])

            df_result = pl.DataFrame()
            if value_list:
                df_result = pl.DataFrame(
                    {
                        "sensor": retrieved_sensors,
                        "time": time_list,
                        "value": value_list,
                    },
                    strict=False,
                )

            if not df_result.is_empty():
                # Fetch metadata if calibration or alias is required and not already fetched
                if (cal or alias) and metadata is None:
                    metadata = await self.get_device_metadata(device_id, on_prem)

                df_result = self.__get_cleaned_table(
                    df=df_result,
                    alias=alias,
                    cal=cal,
                    device_id=device_id,
                    sensor_list=sensor_list,
                    on_prem=on_prem,
                    unix=unix,
                    metadata=metadata,
                )

            return df_result

        except aiohttp.ClientError as e:
            error_message = f"HTTPException: {e}"
            await self.logger.error(error_message, self.extra_params)
            return pl.DataFrame()

        except (TypeError, ValueError) as e:
            error_message = f"Type Error: {type(e).__name__}: {e}"
            await self.logger.error(error_message, self.extra_params)
            return pl.DataFrame()

        except Exception as e:
            error_message = f"Unexpected Exception: {e}"
            await self.logger.critical(error_message, self.extra_params)
            return pl.DataFrame()
