import os
import time
import json

from requests import Response, RequestException
from requests_oauthlib import OAuth2Session

from .logger_client import Logger
from .user_client import UserClient
from .course_client import CourseClient
from .endpoint_client import EndpointClient
from .grade_client import GradeClient
from .discussion_client import DiscussionClient
from .exceptions import ChawkError


class BlackboardClient:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: str,
        log_file: str = "chawk.log",
    ):
        if not all([client_id, client_secret, base_url]):
            raise ChawkError("All parameters for creating client must be provided and not empty.")
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = f"{base_url}/learn/api/public/v1/oauth2/token"
        self.base_url = base_url
        self.token = None
        # TODO: Is there a better way to do this?
        self.token_file = "data/token.json"
        self.expiry_time = None
        self.logger = Logger(log_file)
        self.endpoints = EndpointClient(self.base_url)

        # Create a session object to persist settings across requests
        self.session = OAuth2Session(client_id=self.client_id)
        self.authenticate()
        self.user = UserClient(self)
        self.course = CourseClient(self)
        self.gradebook = GradeClient(self)
        self.discussion = DiscussionClient(self)

    def get_base_url(self) -> str:
        return self.base_url

    def _send_request(self, method, url, **kwargs) -> Response:
        """
        Internal helper method to send HTTP requests.
        """
        self.authenticate()  

        try:
            # Make the HTTP request (GET, POST, PUT, PATCH, DELETE)
            _response = self.session.request(method, url, **kwargs)
        except RequestException as e:
            raise ChawkError(f"Network error during {method} request to {url}: {e}")

        return _response

    def get(self, url, **kwargs):
        """Send a GET request using the authenticated session."""
        return self._send_request("GET", url, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        """Send a POST request using the authenticated session."""
        return self._send_request("POST", url, data=data, json=json, **kwargs)

    def put(self, url, data=None, json=None, **kwargs):
        """Send a PUT request using the authenticated session."""
        return self._send_request("PUT", url, data=data, json=json, **kwargs)

    def patch(self, url, data=None, json=None, **kwargs):
        """Send a PATCH request using the authenticated session."""
        return self._send_request("PATCH", url, data=data, json=json, **kwargs)

    def delete(self, url, **kwargs):
        """Send a DELETE request using the authenticated session."""
        return self._send_request("DELETE", url, **kwargs)

    def _update_header(self):
        self.session.headers.update(
            {"Authorization": f"Bearer {self.token}", "Accept": "application/json"}
        )

    def _load_token(self):
        """
        Load the token from a JSON file if it exists and is valid (not expired).
        """
        if os.path.exists(self.token_file):
            with open(self.token_file, "r") as f:
                token_data = json.load(f)
                self.token = token_data.get("access_token")
                self.expiry_time = token_data.get("expiry_time")
                self._update_header()
                # self.session.headers.update({
                #     "Authorization": f'Bearer {self.token}',
                #     "Accept": "application/json"
                # })
                # If the token is expired, discard it
                if self.expiry_time and time.time() > self.expiry_time:
                    self.logger.info("Token expired, requesting a new one.")
                    self.token = None
                    self.expiry_time = None
                else:
                    self.logger.info("Token loaded from file.")

    def save_token(self):
        """
        Save the token and its expiry time to a JSON file.
        """
        if self.token and self.expiry_time:
            with open(self.token_file, "w") as f:
                json.dump(
                    {"access_token": self.token, "expiry_time": self.expiry_time}, f
                )
            self.logger.info("Token saved to file.")
        else:
            self.logger.info("failed to save file")

    def authenticate(self):
        """
        Authenticate using OAuth2 Client Credentials and store the token in the session.
        """
        self._load_token()
        if not self.token or time.time() > self.expiry_time:
            self.request_new_token()
            self.logger.info("Authenticated successfully.")
        else:
            # Already had a good token
            return

    def request_new_token(self) -> int:
        """
        Request a new OAuth2 token using client credentials flow and store it.
        """

        try:
            # Fetch the OAuth2 token using client credentials flow
            _token_response = self.session.post(
                self.token_url,
                data={"grant_type": "client_credentials"},
                # Basic auth as per client credentials flow
                auth=(self.client_id, self.client_secret),
            )

            # Check for successful response
            if _token_response.status_code == 200:
                self.logger.info("A new token was generated.")
                self.token = _token_response.json()["access_token"]
                _expires_in = _token_response.json()["expires_in"]
                self.expiry_time = (
                    # Subtracting 60 seconds for early refresh
                    time.time() + _expires_in - 60
                )  
                # Update the session's token in the header
                #self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                self._update_header()
                self.save_token()
            else:
                self.logger.critical(f"Failed to get a token. {_token_response.text}")

        except Exception as e:
            self.logger.error(f"Error occurred while fetching token: {e}")

    def get_remaining_calls(self) -> int:
        """Get the remaining number of api calls you can call based on your quota

        Returns:
            int: The number of remaining calls
        """
        # Random endpoint to get a response from
        url = f"{self.base_url}/learn/api/public/v1/users/userName:1000001"
        response = self.session.get(url)
        remaining_requests = response.headers.get("X-Rate-Limit-Remaining")
        if remaining_requests:
            return remaining_requests
        else:
            raise ChawkError("X-Rate-Limit-Remaining header not found.")
