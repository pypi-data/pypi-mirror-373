import json
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typeguard import typechecked
from typing import Optional, Callable, List
from collections import namedtuple

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import pandas as pd
import urllib3
import logging
from io_connect.utilities.store import Logger

import io_connect.constants as c

# Disable pandas' warning about chained assignment
pd.options.mode.chained_assignment = None

# Disable urllib3's warning about insecure requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@typechecked
class MQTTHandler:
    __version__ = c.VERSION
    """Class for managing MQTT communication,
    including publishing data to an MQTT broker
    and handling message processing and client connections."""

    def __init__(
        self,
        username: str,
        password: str,
        host: str,
        port: int,
        logger: Optional[logging.Logger] = None,
    ):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.auth = {"username": self.username, "password": self.password}
        self.topics = None
        self.func = None
        self.logger = Logger(logger)

    def __validate(self, messages: list):
        """
        Validates a list of messages ensuring each has 'topic' and 'payload' keys.

        Args:
            messages (list): List of dictionaries where each dictionary represents a message
                to be validated. Each message dictionary must contain 'topic' and 'payload' keys.

        Raises:
            ValueError: If any message in messages is missing 'topic' or 'payload'.

        Notes:
            This method is used to ensure that each message dictionary contains the necessary
            'topic' and 'payload' keys before attempting to publish them.
        """
        # Iterate over each message in the list to check for required keys
        for message in messages:
            # Check if 'topic' or 'payload' keys are missing in the message dictionary
            if "topic" not in message or "payload" not in message:
                # Raise a ValueError if the message format is invalid
                raise ValueError(f"Invalid message format: {message}")

    def publish_multiple_payload(
        self, messages: list, chunk_size: Optional[int] = c.MAX_CHUNK_SIZE
    ):
        """
        Publishes a list of MQTT messages in chunks to the specified MQTT broker.

        Args:
            messages (list): List of dictionaries where each dictionary represents a message
                to be published. Each message dictionary must contain 'topic' and 'payload' keys.
            chunk_size (Optional[int]): Number of messages to publish per chunk. Defaults to
                c.MAX_CHUNK_SIZE if not specified. Must be a positive integer not exceeding
                the maximum allowed size of 1000.

        Raises:
            ValueError: If chunk_size is not a positive integer or exceeds c.MAX_CHUNK_SIZE,
                or if any message in messages is missing 'topic' or 'payload'.

        Usage:
            Example instantiation:
            >>> mqtt_handler = MQTTHandler(username, password, host, port)

            Example usage of publish_multiple_payload method:
            >>> messages = [{'topic': 'topic1', 'payload': 'data1'}, {'topic': 'topic2', 'payload': 'data2'}]
            >>> mqtt_handler.publish_multiple_payload(messages, chunk_size=50)
            [INFO] Publishing chunk: 0 of 1.
            [INFO] Data Published Successfully!

        Notes:
            This method uses publish.multiple from an MQTT library to efficiently publish
            messages in chunks. It also logs each chunk's progress and handles exceptions,
            printing them to the console if encountered.
        """
        try:
            # Validate chunk size to ensure it is a positive integer and does not exceed the maximum allowed size
            if chunk_size > c.MAX_CHUNK_SIZE or chunk_size <= 0:
                raise ValueError(
                    "Chunk size must be a positive integer and not exceed the maximum allowed size of 1000"
                )

            # Validate the input messages to ensure each message has 'topic' and 'payload' keys
            self.__validate(messages)

            # Calculate the total number of messages and the number of chunks needed
            total_messages = len(messages)
            total_chunks = (total_messages + chunk_size - 1) // chunk_size

            # Iterate over the messages in chunks and publish each chunk
            for i in range(0, total_messages, chunk_size):
                # Log the progress of chunk publishing
                self.logger.display_log(
                    f"[INFO] Publishing chunk: {int(i / chunk_size)} of {total_chunks}."
                )

                # Get the current chunk of messages to be published
                chunk = messages[i : i + chunk_size]

                # Publish the chunk using publish.multiple method from the MQTT library
                publish.multiple(
                    chunk,
                    hostname=self.host,
                    port=self.port,
                    auth=self.auth,
                )

                # Sleep for a defined interval between publishing chunks to avoid overwhelming the broker
                time.sleep(c.SLEEP_TIME)

            # Log success message after all chunks are published
            self.logger.display_log("[INFO] Data Published Successfully!")

        # Handle ValueError if chunk size is invalid or any message is missing 'topic' or 'payload'
        except ValueError as e:
            print(f"[EXCEPTION] {e}")

        # Handle any other exceptions that may occur
        except Exception as e:
            print(f"[EXCEPTION] {e}")

    def publish_single_payload(self, messages: list):
        """
        Publishes a list of MQTT messages individually to the specified MQTT broker.

        Args:
            messages (list): List of dictionaries where each dictionary represents a message
                to be published. Each message dictionary must contain 'topic' and 'payload' keys.

        Raises:
            ValueError: If any message in messages is missing 'topic' or 'payload'.

        Usage:
            Example instantiation:
            >>> mqtt_handler = MQTTHandler(username, password,host, port)

            Example usage of publish_single_payload method:
            >>> messages = [{'topic': 'topic1', 'payload': 'data1'}, {'topic': 'topic2', 'payload': 'data2'}]
            >>> mqtt_handler.publish_single_payload(messages, chunk_size=50)
            [INFO] Publishing message: 0 of 2.
            [INFO] Publishing message: 1 of 2.
            [INFO] Data Published Successfully!

        Notes:
            This method uses publish.single from an MQTT library to publish each message
            individually. It logs each message's progress and handles exceptions, printing
            them to the console if encountered.
        """
        try:
            # Validate the input messages to ensure each message has 'topic' and 'payload' keys
            self.__validate(messages)

            # Get the total number of messages to be published
            total_messages = len(messages)

            # Iterate over each message and publish it
            for index, message in enumerate(messages):
                # Log the progress of message publishing
                self.logger.display_log(
                    f"[INFO] Publishing message: {index} of {total_messages}."
                )

                # Publish the message using publish.single method from the MQTT library
                publish.single(
                    message["topic"],
                    message["payload"],
                    hostname=self.host,
                    port=self.port,
                    auth=self.auth,
                )

            # Log success message after all messages are published
            self.logger.display_log("[INFO] Data Published Successfully!")

        # Handle ValueError if any message is missing 'topic' or 'payload'
        except ValueError as e:
            print(f"[EXCEPTION] {e}")

        # Handle any other exceptions that may occur
        except Exception as e:
            print(f"[EXCEPTION] {e}")

    def payload(
        self,
        topic: str,
        device: str,
        data: List[dict],
        unixtime: Optional[int] = int(datetime.now(c.UTC).timestamp()),
        qos: Optional[int] = 0,
        retain: Optional[bool] = False,
        **kwargs,
    ) -> dict:
        """
        Create a message payload for publishing data with multiple tag-value pairs to a specific topic.

        Args:
            topic (str): The topic to which the message will be published.
            device (str): The device identifier.
            data (list of dict): A list of dictionaries containing tag-value pairs.
            unixtime (int, optional): The UNIX timestamp in seconds. Defaults to the current time in UTC.
            qos (int, optional): The Quality of Service level for message delivery. Defaults to 0.
            retain (bool, optional): Whether the message should be retained by the broker. Defaults to False.
            **kwargs: Additional key-value pairs to include in the payload.

        Returns:
            dict: A dictionary representing the message payload, including the topic, payload data as a JSON string, QoS, and retain flag.

        Example:
            >>> payload = MQTTHandler.payload(
            ...     topic="topic1",
            ...     device='device1',
            ...     data=[{"tag": "DV5176", "value": "2.64"}]
            ... )
            >>> print(payload)
            {'topic': 'topic1', 'payload': '{"device": "device1", "time": 1721714537, "data": [{"tag": "DV516", "value": "2.6570619469026524"}]}', 'qos': 0, 'retain': False}

        Raises:
            TypeError: If arguments are missing or of incorrect type.
            Exception: For other errors that may occur during payload creation.
        """
        try:
            # Create the message payload dictionary
            msg = {
                "topic": topic,
                "payload": json.dumps(
                    {"device": device, "time": unixtime, "data": data, **kwargs}
                ),
                "qos": qos,
                "retain": retain,
            }

            # Return the constructed message payload
            return msg

        # Handle TypeError if arguments are missing or invalid
        except TypeError:
            print(
                "[EXCEPTION] Missing or invalid arguments. Please provide the required arguments in the correct format."
            )
            return {}

        # Handle any other exceptions that may occur
        except Exception as e:
            print(f"[EXCEPTION] Error creating message payload: {e}")
            return {}

    def __process_row(
        self,
        row: namedtuple,
        tag_columns: list,
        extra_keys: set,
        qos: int,
        retain: bool,
    ):
        """
        Process a single row of the DataFrame to generate a payload.

        Args:
            row (namedtuple): A single row of the DataFrame represented as a namedtuple.
            tag_columns (list): A list of column names representing tags in the DataFrame.
            extra_keys (set): A set of additional keys to be included in the message.
            qos (int): The Quality of Service level for message delivery to the MQTT broker.
            retain (bool): Whether the message should be retained by the MQTT broker.

        Returns:
            dict: A dictionary representing the payload for the processed data point.

        This method processes a single row of the DataFrame to generate a payload. It extracts tag values
        from the row, creates data entries for non-null values, and constructs the payload with the
        device identifier, topic, timestamp, and data entries. The payload includes additional key-value
        pairs from the row if specified. The payload is returned as a dictionary.
        """

        # Use list comprehension to build data with non-null attributes
        data = [
            {
                "tag": column,
                "value": getattr(row, column),
            }
            for column in tag_columns
            if pd.notna(getattr(row, column))
        ]

        # Extract extra key-value pairs from the row
        extra_kwargs = {
            key: getattr(row, key) for key in extra_keys if pd.notna(getattr(row, key))
        }

        # Create payload
        return self.payload(
            topic=row.topic,  # Access attribute using dot notation
            device=row.device,  # Access attribute using dot notation
            data=data,
            unixtime=row.unixtime,  # Access attribute using dot notation
            qos=qos,
            retain=retain,
            **extra_kwargs,
        )

    def multiple_payload(
        self,
        df: pd.DataFrame,
        tag_columns: Optional[list] = None,
        qos: Optional[int] = 0,
        retain: Optional[bool] = False,
    ) -> list:
        """
        Generates payloads for multiple data points from a DataFrame using concurrent execution.

        Args:
            df (pd.DataFrame): Input DataFrame containing data points. The DataFrame should include:
                - 'device': Identifier for the device associated with the data point.
                - 'topic': Topic associated with the data point.
                - 'unixtime': Timestamp indicating when the data point was recorded.
                - Other columns represent different tags and their corresponding values for each data point.
            tag_columns (Optional[list]): List of column names to be used as tag columns. If not provided,
                all columns except 'unixtime', 'device', and 'topic' are considered tag columns.
            qos (Optional[int]): Quality of Service level for message delivery to the MQTT broker. Default is 0.
            retain (Optional[bool]): Whether the message should be retained by the MQTT broker. Default is False.

        Returns:
            list: A list of dictionaries, each representing a payload for a data point.

        Example:
            To generate payloads for a DataFrame and print the results:
            >>> import pandas as pd
            >>> # Sample DataFrame
            >>> df = pd.DataFrame({
            ...     'device': ['device1', 'device2', 'device1'],
            ...     'topic': ['topic1', 'topic2', 'topic1'],
            ...     'unixtime': [1619536800, 1619536860, 1619536920],
            ...     'temperature': [25.5, None, 26.3],
            ...     'humidity': [None, 60.0, 65.0]
            ... })
            >>> # Create an instance of the payload generator
            >>> payload_generator = MQTTHandler()
            >>> # Generate payloads for the DataFrame
            >>> payloads = payload_generator.multiple_payload(df=df)
            >>> # Output the generated payloads
            >>> print(payloads)

        This method processes each row of the DataFrame to construct payloads, excluding the 'unixtime', 'device',
        and 'topic' columns from the tag columns. It handles non-null values in tag columns, constructs payloads
        including device identifier, topic, timestamp, and data entries. Columns other than those specified in
        tag_columns are used as keys of the payload and are not considered as tag value pairs in the data.
        The processing of rows is executed concurrently using a thread pool to improve performance.
        The resulting payloads are returned as a list of dictionaries.

        Raises:
            ValueError: If the DataFrame is missing required columns like 'device', 'topic', or 'unixtime'.
            TypeError: If arguments are missing or of incorrect type.
            Exception: For other errors that may occur during payload generation.
        """
        try:
            # Check if all required columns are present in the DataFrame
            required_columns = {"device", "topic", "unixtime"}
            if not required_columns.issubset(df.columns):
                raise ValueError(
                    f"DataFrame must contain the following columns: {required_columns}"
                )

            if not tag_columns:
                # Extract tag columns
                tag_columns = [col for col in df.columns if col not in required_columns]

            print(f"[INFO] Tags detected: {tag_columns}")

            payload_keys = (
                set(df.columns) - set(tag_columns + ["topic", "unixtime"])
            ) | {
                "time",
                "data",
            }

            print(f"[INFO] Payload keys: {payload_keys}")
            extra_keys = set(payload_keys) - set(["time", "data", "device"])

            threads = max(1, len(df) // 5000)

            with ThreadPoolExecutor(max_workers=threads) as executor:
                # Map the processing function to each row of the DataFrame
                # This ensures that the final_payload maintains the order
                final_payload = list(
                    executor.map(
                        lambda row: self.__process_row(
                            row, tag_columns, extra_keys, qos, retain
                        ),
                        df.itertuples(index=False),
                    )
                )
            return final_payload

        except TypeError as e:
            print(
                f"[EXCEPTION] Missing or invalid arguments. Please provide the required arguments in the correct format.{e}"
            )
            return []

        # Handle any exceptions that may occur
        except Exception as e:
            print(f"[EXCEPTION] Error creating payload list: {e}")
            return []

    def report_payload(
        self,
        df: pd.DataFrame,
        topic: str,
        col_drop: bool = False,
        max_chunk_len: int = 10000,
        qos: int = 0,
        retain: bool = False,
    ) -> list:
        """
        Generates payloads for reporting DataFrame content over MQTT.

        Args:
            df (pd.DataFrame): The DataFrame containing the data to be reported.
            topic (str): The MQTT topic to which the payloads will be published.
            drop_columns (bool, optional): Whether to drop DataFrame columns 'device', 'topic', and 'unixtime'. Defaults to False.
            max_chunk_length (int, optional): The maximum length of each chunk of data in the payloads. Defaults to 10000.
            qos (int, optional): The quality of service level for message delivery. Defaults to 0.
            retain (bool, optional): Indicates whether the message should be retained by the broker. Defaults to False.

        Returns:
            A list of message payloads, each containing the following keys:
                - "topic": The MQTT topic to publish the payload.
                - "payload": The JSON payload containing a chunk of data from the DataFrame.
                - "qos": The quality of service level for message delivery.
                - "retain": Indicates whether the message should be retained by the broker.

        Raises:
            TypeError: If there are missing or invalid arguments in the function call.
            Exception: If an error occurs during payload generation.

        Note:
            The function chunks the DataFrame content into smaller segments to avoid message size limitations.

        Example:
            >>> manager = MQTTHandler(USER_NAME,PASSWORD,MQTT_HOST,MQTT_PORT)
            >>> data = {'device': ['device1', 'device2'], 'temperature': [25.5, 30.0], 'humidity': [60, 55]}
            >>> df = pd.DataFrame(data)
            >>> topic = "topic"
            >>> payloads = manager.report_payload(df, topic)
            >>> for payload in payloads:
            ...     print(payload)
        """
        try:
            counter = 1
            payloads = []

            # Check if columns should be dropped from the DataFrame
            if col_drop:
                # Convert the DataFrame to JSON format, resetting the index to handle the drop
                json_str = (
                    df.T.reset_index()
                    .T.reset_index(drop=True)
                    .to_json(orient="records")
                )

            else:
                # Convert the DataFrame to JSON format without dropping columns
                json_str = df.to_json(orient="records")

            # Chunk the JSON string and create payloads
            for i in range(0, len(json_str), max_chunk_len):
                chunk = json_str[i : i + max_chunk_len]  # Extract the current chunk

                # Create the payload object
                payload_obj = {"order": counter, "data": chunk}

                payloads.append(
                    {
                        "topic": topic,
                        "payload": payload_obj,
                        "qos": qos,
                        "retain": retain,
                    }
                )

                # Increment the counter for the next chunk
                counter += 1

            # Return the list of payloads
            return payloads

        except TypeError:
            print(
                "[EXCEPTION] Missing or invalid arguments. Please provide the required arguments in the correct format."
            )
            return []

        # Handle any other exceptions that may occur
        except Exception as e:
            print(f"[EXCEPTION] Error creating report payload: {e}")
            return []

    def __on_connect(
        self,
        client: Optional[mqtt.Client],
        userdata: Optional[object],
        flags: Optional[dict],
        rc: int,
    ):
        """A callback function to be called when the MQTT client is connected to the broker.
        It subscribes to the specified subtopic MQTT topic.

        Args:
            client (mqtt.Client): the MQTT client instance.
            userdata (object): the user data associated with the client.
            flags (dict): a dictionary containing flags representing the connection status.
            rc (int): the result code returned by the broker after the connection attempt.
        """
        try:
            if rc == 0:
                print("\n[INFO] Client Connected")

                for topic in self.topics:
                    client.subscribe(topic, qos=0)
                    print("[INFO] Subscribed to:", topic)
            else:
                print("\n[INFO] Bad Connection: " + str(rc))

        # Handle any exceptions that may occur
        except Exception as e:
            print("[EXCEPTION] ", e)

    def __on_disconnect(
        self, client: Optional[mqtt.Client], userdata: Optional[object], rc: int
    ):
        """A callback function to be called when the MQTT client is disconnected from the broker.
        It prints a message if the disconnection was unexpected.

        Args:
            client (mqtt.Client): the MQTT client instance.
            userdata (object): the user data associated with the client.
            rc (int): the result code returned by the broker after the disconnection.
        """

        try:
            if rc != 0:
                print("\n[INFO] Unexpected Disconnection: " + str(rc))

        # Handle any exceptions that may occur
        except Exception as e:
            print("[EXCEPTION] ", e)

    def __on_message(
        self,
        client: Optional[mqtt.Client],
        userdata: Optional[object],
        message: mqtt.MQTTMessage,
    ):
        """
        A callback function triggered when a message is received on the subscribed MQTT topic.

        This function decodes the received message and spawns a new thread to process the
        message using the `self.func` method.

        Args:
            client (mqtt.Client): The MQTT client instance.
            userdata (object): The user data associated with the client.
            message (mqtt.MQTTMessage): The message received from the broker, containing the payload.

        Exceptions:
            Catches and prints any exceptions that occur during message decoding or thread creation.
        """

        try:
            decoded_msg = message.payload.decode("utf-8")
            threading.Thread(target=lambda: self.func(client, decoded_msg)).start()

        # Handle any exceptions that may occur
        except Exception as e:
            print("[EXCEPTION] ", e)

    def run(self, topics: list, func: Callable):
        """
        Initialize and run the MQTT client to connect to the broker, subscribe to topics, and process incoming messages.

        This method sets up the MQTT client with the provided topics and callback function. It handles connection, message reception, and disconnection events. The client runs in an infinite loop to continuously listen for incoming messages.

        Args:
            topics (list): A list of topics to subscribe to. Each topic in the list should be a string representing the topic name.
            func (Callable): A callback function to handle incoming messages. This function should accept two arguments:
                             - topic (str): The topic on which the message was received.
                             - message (str): The message payload received on the topic.

        Raises:
            Exception: Captures and prints any exception that occurs during the setup or execution of the MQTT client.

        Example:
            >>> def message_handler(topic, message):
            >>>     print(f"Received message on {topic}: {message}")
            >>>
            >>> mqtt_handler = MQTTHandler(USER_NAME,PASSWORD,MQTT_HOST,MQTT_PORT)
            >>> mqtt_handler.run(topics=["topic/1", "topic/2"], func=message_handler)
        """
        try:
            self.topics = topics
            self.func = func
            client = mqtt.Client(str(uuid.uuid1()))
            client.username_pw_set(self.username, self.password)
            client.on_connect = self.__on_connect
            client.on_message = self.__on_message
            client.on_disconnect = self.__on_disconnect

            client.connect(self.host, self.port)
            client.loop_forever()

        # Handle any exceptions that may occur
        except Exception as e:
            print("[EXCEPTION] ", e)
