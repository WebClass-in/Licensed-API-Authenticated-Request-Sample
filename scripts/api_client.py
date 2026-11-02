import requests
from urllib.parse import urlsplit

from authenticator import HMACAuthenticator


class LicensedAPIClient:

    def __init__(self, config):
        self.config = config

    def post(self, endpoint):

        parsed_url = urlsplit(endpoint)

        method = "POST"
        path = parsed_url.path
        query_string = parsed_url.query
        body = b""

        signature = HMACAuthenticator.generate_signature(
            self.config.api_secret,
            method,
            path,
            query_string,
            body
        )

        headers = {
            "X-API-KEY": self.config.api_key,
            "X-API-SIGNATURE": signature
        }

        response = requests.post(
            endpoint,
            headers=headers,
            data=body
        )

        return response