#!/usr/bin/env python
"""Core API Class Object."""

import logging
import warnings
from getpass import getpass
from os import environ
from time import ctime, time
from typing import Any, Dict, List, Optional, Tuple

import jwt
import requests
import requests.adapters
from urllib3.util import Retry

from chime_frb_api.core.exceptions import ConfigurationError, TokenError

# Configure Logger
LOGGING_FORMAT = "[%(asctime)s] %(levelname)s "
LOGGING_FORMAT += "%(message)s"
logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO)
log = logging.getLogger(__name__)


class API:
    """Application Programming Interface Base Class."""

    def __init__(self, debug: bool = False, **kwargs):
        """CHIME/FRB Core API Initialization.

        Args:
            self : API
                API Class Object
            debug : bool, optional
                Enable debug logging, by default False
            **kwargs: dict

            base_url : str
                Base URL for CHIME/FRB Master
            access_token : str
                Access token for authentiation
            refresh_token : str
                Refresh token to authentiation
            username : str
                CHIME username
            password : str
                CHIME password

        Raises:
            APIError
                CHIME/FRB API Error
        """
        if debug:
            log.setLevel(logging.DEBUG)
        # base_url is set automatically now
        self.base_urls = kwargs.get("default_base_urls", [])
        if not debug:
            # Construct list of possible base_urls
            if kwargs.get("base_url"):
                self.base_urls.insert(0, kwargs.get("base_url"))
            self.base_url = self._select_base_url(self.base_urls)
        else:
            log.warning("Debug Mode: Ignoring default base URLS")
            self.base_url = kwargs.get("base_url", None)

        # Create a requests session
        self._session = requests.Session()
        # Enable / Disable authentication
        self.authentication = kwargs.get("authentication", True)
        # Collect authentiation parameters if they were initialized
        self.access_token = kwargs.get("access_token", None)
        self.refresh_token = kwargs.get("refresh_token", None)
        self.username = kwargs.get("username", None)
        self.password = kwargs.get("password", None)
        # State Variables
        self.authorized = False
        self.expire_time = 0
        # Get configuration parameters from env
        self._config_from_env()
        self._check_configuration()
        self._prepare_session()

    def _prepare_session(self):
        """Prepare the HTTP Session for retries."""
        retry_strategy = Retry(
            total=10, status_forcelist=[502, 503, 504], backoff_factor=2
        )
        adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

    def _config_from_env(self, environment: Optional[dict] = None) -> None:
        """Get configuration parameters from os environment.

        Args:
            self: API Class Object
            environment: environment variables, defaults to None.
        """
        if not environment:
            environment = dict(environ)

        if environ.get("CHIME_FRB_ACCESS_TOKEN"):
            self.access_token = environ.get("CHIME_FRB_ACCESS_TOKEN")
        elif environ.get("FRB_MASTER_ACCESS_TOKEN"):
            self.access_token = environ.get("FRB_MASTER_ACCESS_TOKEN")
            log.warning(
                "The FRB_MASTER_ACCESS_TOKEN environment variable will "
                "be deprecated in future versions. Rename to "
                "CHIME_FRB_ACCESS_TOKEN instead."
            )
        else:
            self.access_token = None
            log.debug("No access token found in environment.")

        if environ.get("CHIME_FRB_REFRESH_TOKEN"):
            self.refresh_token = environ.get("CHIME_FRB_REFRESH_TOKEN")
        elif environ.get("FRB_MASTER_REFRESH_TOKEN"):
            log.warning(
                "The FRB_MASTER_REFRESH_TOKEN environment variable will "
                "be deprecated in future versions. Rename to "
                "CHIME_FRB_REFRESH_TOKEN instead."
            )
            self.refresh_token = environ.get("FRB_MASTER_REFRESH_TOKEN")
        else:
            self.refresh_token = None
            log.debug("No refresh token found in environment.")

        if not self.username:
            self.username = environ.get("FRB_MASTER_USERNAME", None)

        if not self.password:
            self.password = environ.get("FRB_MASTER_PASSWORD", None)

    def _select_base_url(self, base_urls: List[str]) -> str:
        """Find the optimal base_url for HTTP Requests Session.

        Args:
            self: API Class Object
            base_urls: List of base_urls to test

        Returns:
            The base_url that responds with HTML code 200.
        """
        successful: bool = False
        for base_url in base_urls:
            try:
                response = requests.get(base_url + "/version", timeout=1)
                if response.status_code == 200:
                    log.debug(f"base url: {base_url}")
                    version = response.json().get("version")
                    log.debug(f"version : {version}")
                    successful = True
                    break
            except Exception as error:  # pragma: no cover
                log.debug(f"unable to connect @ {base_url}")
                log.debug(error)
        if not successful:
            raise ConfigurationError("unable to connect to any base url")
        return str(base_url)

    def _check_configuration(self):
        """Check minimum configuration parameters.

        Args:
            self: API Class Object

        Raises:
            ConfigurationError: base_url not configured.
        """
        if not self.base_url:
            raise ConfigurationError("base_url not configured")

    def _coalesse_parameters(
        self,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
        """Coalesse passed and configured parameters.

        Args:
            self: API Class Object
            access_token: Access token for authentiation
            refresh_token: Refresh token to authentiation
            username: CHIME username
            password: CHIME password

        Returns:
            Tuple of access_token, refresh_token, username, password
        """
        # Gather authentication parameters if none were provided
        if not access_token:
            access_token = self.access_token
        if not refresh_token:
            refresh_token = self.refresh_token
        if not username:
            username = self.username
        if not password:
            password = self.password
        return access_token, refresh_token, username, password

    def _get_user_details(
        self, username: Optional[str] = None, password: Optional[str] = None
    ) -> Tuple[str, str]:
        """Get user details from terminal input.

        Args:
            self: API Class Object
            username: CHIME username
            password: CHIME password

        Returns:
            Tuple of username, password
        """
        if not username:  # pragma: no cover
            username = input("Username: ")
            # Save username for future uses
            self.username = username
        if not password:  # pragma: no cover
            # Get the password if we don't have it
            password = getpass("Password: ")
        return username, password

    def _check_authorization(self):
        """Check CHIME/FRB API Authorization Status.

        Args:
            self: API Class Object
        """
        if self.authorized:
            # If authorized, check if access_token is valid
            if self.expire_time < time():  # pragma: no cover
                log.debug("Authorization Status: Expired")
                self.reauthorize()
            else:
                log.debug("Authorization Status: Active")
        else:
            # If not currently authorized, do it.
            log.info("Authorization Status: None")
            self.authorize()

    def _set_expire_time(self):
        """Decode the JWT and find when it will expire."""
        try:
            self.expire_time = jwt.decode(self.access_token, verify=False).get(
                "exp", 0
            )
            log.debug(f"Authorization Expiry: {ctime(self.expire_time)}")
        except Exception as e:  # pragma: no cover
            log.warning(e)

    def _deprecation(self, message: str):  # pragma: no cover
        """Depration Warning.

        Args:
            self: API Class Object
            message: Message to display
        """
        warnings.warn(message, DeprecationWarning, stacklevel=2)
        log.warning(message)

    ###########################################################################
    def authorize(
        self,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> bool:
        """Authorize user.

        Args:
            access_token: CHIME/FRB Master JWT Token
            refresh_token: CHIME/FRB Refresh Token
            username: CHIME/FRB Username
            password: CHIME/FRB Password

        Returns:
            Result of the authorization in boolean format.
        """
        try:
            access_token, refresh_token, username, password = (
                self._coalesse_parameters(
                    access_token, refresh_token, username, password
                )
            )
            # We already have access_token, check if it is valid
            if access_token:
                log.info("Authorization Method: Tokens")
                self._session.headers.update(authorization=access_token)
                response = self._session.get(self.base_url + "/auth/verify")
                # If response is good, return True
                if response.json().get("valid", False):
                    log.info("Authorization Result: Passed")
                    # Deposit Tokens
                    self.access_token = access_token
                    self.refresh_token = refresh_token
                    self._set_expire_time()
                    self.authorized = True
                    return True
                # Check if we have refresh token
                elif refresh_token:
                    log.info("Authorization Token : Expired")
                    # If reauth was successful, return True
                    if self.reauthorize():  # pragma: no cover
                        self.authorized = True
                        return True
                else:  # pragma: no cover
                    log.warning("Token Authorization Failed")
                    # Remove bad
                    self._session.headers.pop("authorization", None)
                    self.authorized = False
                    log.warning("Generate new tokens to continue.")
            return False

        except requests.exceptions.RequestException as e:
            log.error("Authorization Failed")
            self.expire_time = 0
            self.authorized = False
            self._session.headers.pop("authorization", None)
            log.error(e)
            raise e
            return False

    def reauthorize(
        self,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
    ) -> bool:
        """Re-authentication.

        Args:
            access_token: CHIME/FRB Master JWT Token
            refresh_token: CHIME/FRB Refresh Token

        Returns:
            Result of the authorization in boolean format.

        Raises:
            RequestException: Unable to authenticate.
        """
        access_token, refresh_token, username, password = (
            self._coalesse_parameters(access_token, refresh_token)
        )
        try:
            return self._reauthorize(refresh_token, access_token)
        except requests.exceptions.RequestException as error:
            log.error("Re-authorize Result: Failed")
            self.access_token = None
            self.refresh_token = None
            self.expire_time = 0
            self.authorized = False
            raise error

    def _reauthorize(self, refresh_token, access_token):
        if not refresh_token and not access_token:
            raise TokenError("missing: refresh_token or access_token")
        log.info("Reauthorize Method: Tokens")
        self._session.headers.update(authorization=access_token)
        payload = {}
        payload.update(refresh_token=refresh_token)
        response = self._session.post(
            self.base_url + "/auth/refresh", json=payload
        )
        response.raise_for_status()
        tokens = response.json()
        log.debug(tokens)
        self.access_token = tokens.get("access_token", None)
        self.refresh_token = refresh_token
        self._set_expire_time()
        self._session.headers.update(authorization=self.access_token)
        log.info("Reauthorize Result: Passed")
        return True

    def generate_token(
        self, username: Optional[str] = None, password: Optional[str] = None
    ) -> bool:
        """Generate a new JWT token.

        Args:
            username: CHIME/FRB Username
            password: CHIME/FRB Password

        Returns:
            Result of the token generation in boolean format.
        """
        # Check if username and password are provided
        if username is None and password is None:
            username, password = self._get_user_details(
                username=username, password=password
            )
        payload: Dict[str, Any] = {}
        payload.update(username=username, password=password)
        # Query for authentiation
        response = self._session.post(url=self.base_url + "/auth", json=payload)
        response.raise_for_status()
        log.info("Authorization Result: Passed")
        tokens = response.json()
        print(
            "Please add your new tokens to your environment using the following:"
        )
        log.debug(tokens)
        print(
            f'export CHIME_FRB_ACCESS_TOKEN="{tokens.get("access_token", None)}"'
        )
        self.access_token = tokens.get("access_token", None)
        print(
            f'export CHIME_FRB_REFRESH_TOKEN="{tokens.get("refresh_token", None)}"'
        )
        self.refresh_token = tokens.get("refresh_token", None)
        self._session.headers.update(authorization=self.access_token)
        self._set_expire_time()
        self.authorized = True
        return True

    ###########################################################################
    def post(self, url: str, **kwargs) -> Any:
        """HTTP Post.

        Args:
            url: HTTP URL
            **kwargs: Keyworded arguments synonmous to requests.post

        Returns:
            JSON encoded server response.

        Raises:
            requests.exceptions.RequestException
        """
        try:
            if self.authentication:
                self._check_authorization()
            response = self._session.post(self.base_url + url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as err:
            raise err

    def patch(self, url: str, **kwargs) -> Any:
        """HTTP Patch.

        Args:
            url: HTTP URL
            **kwargs: Keyworded arguments synonmous to requests.patch

        Returns:
            JSON encoded server response.

        Raises:
            requests.exceptions.RequestException
        """
        try:
            if self.authentication:
                self._check_authorization()
            response = self._session.patch(self.base_url + url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as err:  # pragma: no cover
            raise err

    def get(self, url: str, **kwargs) -> Any:
        """HTTP GET.

        Args:
            url: HTTP URL
            **kwargs: Keyworded arguments synonmous to requests.get

        Returns:
            JSON encoded server response.

        Raises:
            requests.exceptions.RequestException
        """
        try:
            if self.authentication:
                self._check_authorization()
            response = self._session.get(self.base_url + url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as err:
            raise err

    def delete(self, url: str, **kwargs) -> Any:
        """HTTP DELETE.

        Args:
            url: HTTP URL
            **kwargs: Keyworded arguments synonmous to requests.delete

        Returns:
            JSON encoded server response.

        Raises:
            requests.exceptions.RequestException
        """
        try:
            if self.authentication:  # pragma: no cover
                self._check_authorization()
            response = self._session.delete(self.base_url + url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as err:
            raise err

    def put(self, url: str, **kwargs) -> Any:
        """HTTP PUT.

        Args:
            url: HTTP URL
            **kwargs: Keyworded arguments synonmous to requests.put

        Returns:
            JSON encoded server response.

        Raises:
            requests.exceptions.RequestException
        """
        try:
            if self.authentication:
                self._check_authorization()
            response = self._session.put(self.base_url + url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as err:
            raise err

    def stream(self, url: str, request_type: str, **kwargs) -> Any:
        """HTTP Stream.

        Args:
            url: HTTP URL
            request_type: HTTP Request Type
            **kwargs: Keyworded arguments synonmous to requests.put

        Returns:
            JSON encoded server response.

        Raises:
            requests.exceptions.RequestException
        """
        try:  # pragma: no cover
            if self.authentication:
                self._check_authorization()
            if request_type == "POST":
                response = self._session.post(
                    self.base_url + url, stream=True, **kwargs
                )
            elif request_type == "GET":
                response = self._session.get(self.base_url + url, **kwargs)
            else:
                raise ConfigurationError(
                    "request_type ['POST' or 'GET'] is required."
                )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as err:  # pragma: no cover
            raise err
