# -*- coding: utf-8 -*-
"""
OpenAlgo REST API Documentation - Base API Class
    https://docs.openalgo.in
"""

import httpx

class BaseAPI:
    """
    Base class to handle all the API calls to OpenAlgo.
    """

    def __init__(self, api_key, host="http://127.0.0.1:5000", version="v1"):
        """
        Initialize the api object with an API key and optionally a host URL and API version.

        Attributes:
        - api_key (str): User's API key.
        - host (str): Base URL for the API endpoints. Defaults to localhost.
        - version (str): API version. Defaults to "v1".
        """
        self.api_key = api_key
        self.base_url = f"{host}/api/{version}/"
        self.headers = {
            'Content-Type': 'application/json'
        }
