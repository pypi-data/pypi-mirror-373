import requests
from typeguard import typechecked
import io_connect.constants as c
from typing import Optional
from io_connect.utilities.store import ERROR_MESSAGE, Logger
import logging


@typechecked
class AlertsHandler:
    __version__ = c.VERSION
    """
    Handles sending alerts via email and Microsoft Teams.

    This class provides methods to send alerts via email and Microsoft Teams using the specified ds_url.

    Attributes:
        ds_url (str): The ds_url name used for constructing URLs for email and Microsoft Teams endpoints.

    Methods:
        notify_email(subject, message, recipient_email):
            Sends an email alert with the specified subject and message content to the provided list of recipients.

        notify_teams(subject, message, recipient_email, origin, service_id, criticality=0):
            Sends an alert message to Microsoft Teams with the specified parameters.
    """

    def __init__(
        self,
        ds_url: str,
        log_time: Optional[bool] = False,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initializes an instance of AlertsHandler with the specified ds_url.

        Args:
            ds_url (str): The ds_url name used for constructing URLs for email and Microsoft Teams endpoints.

        Attributes:
            ds_url (str): The ds_url where the messenger service is hosted.
            __mail_url (str): The URL for sending mail messages.
            __teams_url (str): The URL for sending Teams alerts.

        """
        self.ds_url = ds_url
        self.log_time = log_time
        self.logger = Logger(logger)

    def notify_email(self, subject: str, message: str, recipient_email: list):
        """
        Sends an email alert.

        This function sends an email alert with the specified subject and message content to the provided list of recipients.

        Args:
            subject (str): The subject of the email.
            message (str): The body/message of the email.
            recipient_email (list): A list of email addresses of the recipients.

        Returns:
            bool: True if the email was sent successfully, False otherwise.

        Example:
            To send an email alert about system maintenance to multiple recipients:
            >>> alerts_handler = AlertsHandler(ds_url='203.0.113.0')
            >>> alerts_handler.notify_email(
            ...     subject="System Maintenance Notification",
            ...     message="Our system will undergo maintenance from 10 PM to 12 AM. Please plan accordingly.",
            ...     recipient_email=["user1@example.com", "user2@example.com"]
            ... )
        """

        try:
            # Prepare request payload
            payload = {
                "subject": subject,
                "message": message,
                "receivers": recipient_email,
            }

            url = c.MAIL_URL.format(ds_url=self.ds_url)

            with Logger(self.logger, f"API {url} response time:", self.log_time):
                # Send POST request to the email service URL
                response = requests.post(url, json=payload)

            # Raise an error if the request was not successful
            response.raise_for_status()

            # Return True if the request was successful, False otherwise
            return response.ok

        except requests.exceptions.RequestException as e:
            # Log the error
            error_message = (
                ERROR_MESSAGE(response, url)
                if "response" in locals()
                else f"\n[URL] {url}\n[EXCEPTION] {e}"
            )
            self.logger.error(f"[EXCEPTION] {type(e).__name__}: {error_message}")

            # Return False to indicate failure
            return response.ok

        except Exception as e:
            self.logger.error(f"[EXCEPTION] {e}")
            return False

    def notify_teams(
        self,
        subject: str,
        message: str,
        recipient_email: dict,
        origin: str,
        service_id: str,
        criticality: Optional[int] = 0,
    ):
        """
        Sends an alert message via Microsoft Teams.

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
            >>> alerts_handler = AlertsHandler(ds_url='203.0.113.0')
            >>> alerts_handler.notify_teams(
            ...     subject="Exception in PUBLISHER",
            ...     message="Add exception here or some other error logs which is to be visible in Alert.",
            ...     recipient_email={"Henil Jain": "henil.j@iosense.io"} # Add more names if required.
            ...     origin="Data Publishers",
            ...     service_id="PUBLISHER_12"
            ... )

        """
        try:
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

            with Logger(self.logger, f"API {url} response time:", self.log_time):
                # Send a POST request to the Microsoft Teams URL with the payload in JSON format
                response = requests.post(url, json=payload)

            # Raise an error if the request was not successful
            response.raise_for_status()

            # Return True if the request was successful, False otherwise
            return response.ok

        except requests.exceptions.RequestException as e:
            # Log the error
            error_message = (
                ERROR_MESSAGE(response, url)
                if "response" in locals()
                else f"\n[URL] {url}\n[EXCEPTION] {e}"
            )
            self.logger.error(f"[EXCEPTION] {type(e).__name__}: {error_message}")

            # Return False to indicate failure
            return response.ok

        except Exception as e:
            self.logger.error(f"[EXCEPTION] {e}")
            return False
