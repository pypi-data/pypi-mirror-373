"""This module provides a client for the J-Quants API.

It handles authentication and provides methods to interact with
the API endpoints.
"""

from __future__ import annotations

import datetime
import os
from enum import StrEnum
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING

import polars as pl
from dotenv import load_dotenv, set_key
from httpx import Client
from platformdirs import user_config_dir
from polars import DataFrame

if TYPE_CHECKING:
    from collections.abc import Iterator
    from typing import Any

    from httpx import HTTPStatusError  # noqa: F401
    from httpx._types import QueryParamTypes

API_VERSION = "v1"


class AuthenticationError(Exception):
    """Custom exception for authentication failures."""


class AuthKey(StrEnum):
    """Environment variable keys for J-Quants authentication."""

    REFRESH_TOKEN = "JQUANTS_REFRESH_TOKEN"  # noqa: S105
    ID_TOKEN = "JQUANTS_ID_TOKEN"  # noqa: S105


class JQuantsClient:
    """A client for interacting with the J-Quants API.

    This client manages API authentication tokens (refresh and ID)
    and provides methods to access various J-Quants API
    endpoints. Tokens are loaded from and saved to a file in the
    user's standard config directory.

    Attributes:
        client: An httpx.Client instance for making API requests.
        refresh_token: The refresh token for authentication.
        id_token: The ID token for API requests.
    """

    client: Client
    refresh_token: str | None
    id_token: str | None

    def __init__(self) -> None:
        """Initializes the JQuantsClient.

        It sets up the httpx client, determines the config path,
        loads authentication tokens, and sets the auth header if an
        ID token is present.
        """
        self.client = Client(base_url=f"https://api.jquants.com/{API_VERSION}")
        self._setup_config_path()
        self._load_tokens()
        self.set_header()

    @cached_property
    def dotenv_path(self) -> Path:
        """Returns the path to the .env file in the user config directory."""
        config_dir = Path(user_config_dir("kabukit"))
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / ".env"

    def _setup_config_path(self) -> None:
        """Determines the config path and creates the directory."""
        # Accessing dotenv_path property will create the directory if it doesn't exist
        _ = self.dotenv_path

    def _load_tokens(self) -> None:
        """Loads tokens from the .env file."""
        load_dotenv(self.dotenv_path)
        self.refresh_token = os.environ.get(AuthKey.REFRESH_TOKEN)
        self.id_token = os.environ.get(AuthKey.ID_TOKEN)

    def set_header(self) -> None:
        """Sets the Authorization header if an ID token is available."""
        if self.id_token:
            self.client.headers["Authorization"] = f"Bearer {self.id_token}"
        # Clear header if no ID token is available
        elif "Authorization" in self.client.headers:
            del self.client.headers["Authorization"]

    def auth(self, mailaddress: str, password: str) -> None:
        """Authenticates, saves tokens, and sets the auth header.

        Args:
            mailaddress: The user's email address.
            password: The user's password.

        Raises:
            HTTPStatusError: If any API request fails.
        """
        self.refresh_token = self.get_refresh_token(mailaddress, password)
        self.id_token = self.get_id_token(self.refresh_token)
        set_key(self.dotenv_path, AuthKey.REFRESH_TOKEN, self.refresh_token)
        set_key(self.dotenv_path, AuthKey.ID_TOKEN, self.id_token)
        self.set_header()

    def post(self, url: str, json: Any | None = None) -> Any:
        """Sends a POST request to the specified URL.

        Args:
            url: The URL path for the POST request.
            json: The JSON payload for the request body.

        Returns:
            The JSON response from the API.

        Raises:
            AuthenticationError: If no ID token is available.
            HTTPStatusError: If the API request fails.
        """
        if not self.id_token:
            msg = "ID token is not available. Please authenticate first."
            raise AuthenticationError(msg)

        resp = self.client.post(url, json=json)
        resp.raise_for_status()
        return resp.json()

    def get_refresh_token(self, mailaddress: str, password: str) -> str:
        """Gets a new refresh token from the API.

        Args:
            mailaddress: The user's email address.
            password: The user's password.

        Returns:
            The new refresh token.

        Raises:
            httpx.HTTPStatusError: If the API request fails.
        """
        json_data = {"mailaddress": mailaddress, "password": password}
        return self.post("/token/auth_user", json=json_data)["refreshToken"]

    def get_id_token(self, refresh_token: str) -> str:
        """Gets a new ID token from the API.

        Args:
            refresh_token: The refresh token to use.

        Returns:
            The new ID token.

        Raises:
            HTTPStatusError: If the API request fails.
        """
        url = f"/token/auth_refresh?refreshtoken={refresh_token}"
        return self.post(url)["idToken"]

    def get(self, url: str, params: QueryParamTypes | None = None) -> Any:
        """Sends a GET request to the specified URL.

        Args:
            url: The URL path for the GET request.
            params: The query parameters for the request.

        Returns:
            The JSON response from the API.

        Raises:
            AuthenticationError: If no ID token is available.
            HTTPStatusError: If the API request fails.
        """
        if not self.id_token:
            msg = "ID token is not available. Please authenticate first."
            raise AuthenticationError(msg)

        resp = self.client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def get_listed_info(
        self,
        code: str | None = None,
        date: str | datetime.date | None = None,
    ) -> DataFrame:
        """Gets listed info (e.g., stock details) from the API.

        Args:
            code: Optional. The stock code to filter by.
            date: Optional. The date to filter by (YYYY-MM-DD format
                or datetime.date object).

        Returns:
            A Polars DataFrame containing the listed info.

        Raises:
            AuthenticationError: If no ID token is available.
            HTTPStatusError: If the API request fails.
        """
        params = params_code_date(code, date)
        url = "/listed/info"
        data = self.get(url, params)
        df = DataFrame(data["info"])
        return df.with_columns(pl.col("Date").str.to_date())

    def iter_pagaes(
        self,
        url: str,
        params: dict[str, Any] | None,
        name: str,
    ) -> Iterator[DataFrame]:
        """Iterates through paginated API responses.

        Args:
            url: The base URL for the API endpoint.
            params: Optional. Dictionary of query parameters.
            name: The key in the JSON response containing the list of items.

        Yields:
            A Polars DataFrame for each page of data.

        Raises:
            AuthenticationError: If no ID token is available.
            HTTPStatusError: If the API request fails.
        """
        params = params or {}

        while True:
            data = self.get(url, params)
            yield DataFrame(data[name])
            if "pagination_key" in data:
                params["pagination_key"] = data["pagination_key"]
            else:
                break

    def get_prices(
        self,
        code: str | None = None,
        date: str | datetime.date | None = None,
        from_: str | datetime.date | None = None,
        to: str | datetime.date | None = None,
    ) -> DataFrame:
        """Gets daily stock prices from the API.

        Args:
            code: Optional. The stock code to filter by.
            date: Optional. The specific date for which to retrieve prices.
                Cannot be used with `from_` or `to`.
            from_: Optional. The start date for a price range.
                Requires `to` if `date` is not specified.
            to: Optional. The end date for a price range.
                Requires `from_` if `date` is not specified.

        Returns:
            A Polars DataFrame containing daily stock prices.

        Raises:
            ValueError: If both `date` and `from_`/`to` are specified.
            AuthenticationError: If no ID token is available.
            HTTPStatusError: If the API request fails.
        """
        params = params_code_date(code, date)

        if date and (from_ or to):
            msg = "Cannot specify both date and from/to parameters."
            raise ValueError(msg)

        if not date and from_:
            params["from"] = date_to_str(from_)
        if not date and to:
            params["to"] = date_to_str(to)

        url = "/prices/daily_quotes"
        name = "daily_quotes"

        df = pl.concat(self.iter_pagaes(url, params, name))
        if df.is_empty():
            return df

        return df.with_columns(pl.col("Date").str.to_date())


def params_code_date(
    code: str | None,
    date: str | datetime.date | None,
) -> dict[str, str]:
    """Constructs a dictionary of parameters for code and date filtering.

    Args:
        code: Optional. The stock code.
        date: Optional. The date (string or datetime.date object).

    Returns:
        A dictionary containing 'code' and/or 'date' parameters.
    """
    params: dict[str, str] = {}
    if code:
        params["code"] = code
    if date:
        params["date"] = date_to_str(date)
    return params


def date_to_str(date: str | datetime.date) -> str:
    """Converts a date object or string to a YYYY-MM-DD string.

    Args:
        date: The date to convert (string or datetime.date object).

    Returns:
        The date as a YYYY-MM-DD string.
    """
    if isinstance(date, datetime.date):
        return date.strftime("%Y-%m-%d")
    return date
