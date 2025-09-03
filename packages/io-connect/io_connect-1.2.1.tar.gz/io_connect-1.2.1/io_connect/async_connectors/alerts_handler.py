import aiohttp
import asyncio
from typeguard import typechecked
import io_connect.constants as c
from typing import Optional


@typechecked
class AsyncAlertsHandler:
    __version__ = c.VERSION
    """
    Async version of AlertsHandler for sending alerts via email and Microsoft Teams.

    This class provides async methods to send alerts via email and Microsoft Teams using the specified ds_url.

    Attributes:
        ds_url (str): The ds_url name used for constructing URLs for email and Microsoft Teams endpoints.
        session (aiohttp.ClientSession): Async HTTP client session for making requests.
        timeout (aiohttp.ClientTimeout): Timeout configuration for HTTP requests.

    Methods:
        async notify_email(subject, message, recipient_email):
            Sends an email alert with the specified subject and message content to the provided list of recipients.

        async notify_teams(subject, message, recipient_email, origin, service_id, criticality=0):
            Sends an alert message to Microsoft Teams with the specified parameters.
    """

    def __init__(
        self,
        ds_url: str,
        timeout: Optional[int] = 30,
    ):
        """
        Initializes an instance of AsyncAlertsHandler with the specified ds_url.

        Args:
            ds_url (str): The ds_url name used for constructing URLs for email and Microsoft Teams endpoints.
            timeout (int, optional): Request timeout in seconds. Defaults to 30.

        Attributes:
            ds_url (str): The ds_url where the messenger service is hosted.
            timeout (aiohttp.ClientTimeout): Timeout configuration for HTTP requests.
            _session (aiohttp.ClientSession): Private HTTP client session.
        """
        self.ds_url = ds_url
        self.timeout = aiohttp.ClientTimeout(total=timeout)
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
            self._session = aiohttp.ClientSession(timeout=self.timeout)

    async def close(self):
        """
        Closes the HTTP session gracefully.
        """
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def notify_email(self, subject: str, message: str, recipient_email: list):
        """
        Sends an email alert asynchronously.

        This function sends an email alert with the specified subject and message content to the provided list of recipients.

        Args:
            subject (str): The subject of the email.
            message (str): The body/message of the email.
            recipient_email (list): A list of email addresses of the recipients.

        Returns:
            bool: True if the email was sent successfully, False otherwise.

        Example:
            To send an email alert about system maintenance to multiple recipients:
            >>> async with AsyncAlertsHandler(ds_url='203.0.113.0') as alerts_handler:
            ...     success = await alerts_handler.notify_email(
            ...         subject="System Maintenance Notification",
            ...         message="Our system will undergo maintenance from 10 PM to 12 AM. Please plan accordingly.",
            ...         recipient_email=["user1@example.com", "user2@example.com"]
            ...     )
        """
        response = None
        url = None
        
        try:
            await self._ensure_session()
            
            # Prepare request payload
            payload = {
                "subject": subject,
                "message": message,
                "receivers": recipient_email,
            }

            url = c.MAIL_URL.format(ds_url=self.ds_url)
            
            # Send POST request to the email service URL
            async with self._session.post(url, json=payload) as response:
                response_text = await response.text()

                # Raise an error if the request was not successful
                response.raise_for_status()

                # Return True if the request was successful
                return response.ok

        except aiohttp.ClientError as e:
            # Return False to indicate failure
            return False

        except Exception as e:
            return False

    async def notify_teams(
        self,
        subject: str,
        message: str,
        recipient_email: dict,
        origin: str,
        service_id: str,
        criticality: Optional[int] = 0,
    ):
        """
        Sends an alert message via Microsoft Teams asynchronously.

        This function sends an alert message to Microsoft Teams using the specified parameters.

        Args:
            subject (str): The subject of the alert message.
            message (str): The body/content of the alert message.
            recipient_email (dict): A dictionary containing the names and email addresses of the recipients.
            origin (str): The origin/source of the alert.
            service_id (str): The ID of the service generating the alert.
            criticality (int, optional): The criticality level of the alert. Default is 0.

        Returns:
            bool: True if the alert message was sent successfully, False otherwise.

        Example:
            To send an alert about an exception in UNO_S1 service:
            >>> async with AsyncAlertsHandler(ds_url='203.0.113.0') as alerts_handler:
            ...     success = await alerts_handler.notify_teams(
            ...         subject="Exception in PUBLISHER",
            ...         message="Add exception here or some other error logs which is to be visible in Alert.",
            ...         recipient_email={"Henil Jain": "henil.j@iosense.io"} # Add more names if required.
            ...         origin="Data Publishers",
            ...         service_id="PUBLISHER_12"
            ...     )
        """
        response = None
        url = None
        
        try:
            await self._ensure_session()
            
            # Prepare request payload
            payload = {
                "subject": subject,
                "message": message,
                "receivers": recipient_email,
                "origin": origin,
                "serviceID": service_id,
                "criticality": criticality,
            }

            url = c.TEAMS_URL.format(ds_url=self.ds_url)

            # Send a POST request to the Microsoft Teams URL with the payload in JSON format
            async with self._session.post(url, json=payload) as response:
                response_text = await response.text()

                # Raise an error if the request was not successful
                response.raise_for_status()

                # Return True if the request was successful
                return response.ok

        except aiohttp.ClientError as e:
            # Return False to indicate failure
            return False

        except Exception as e:
            return False

    def __del__(self):
        """
        Destructor to ensure session is closed.
        """
        if self._session and not self._session.closed:
            # Note: In a real async environment, you should use await self.close()
            # This is just a fallback for cleanup
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.close())
                else:
                    loop.run_until_complete(self.close())
            except:
                pass  # Ignore errors during cleanup 