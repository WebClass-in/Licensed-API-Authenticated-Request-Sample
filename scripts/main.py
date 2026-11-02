from config import APIConfig
from api_client import LicensedAPIClient


def main():

    config = APIConfig(
        base_url="xxxxxx",
        api_key="xxxxxx",
        api_secret="xxxxxx"
    )

    client = LicensedAPIClient(config)

    response = client.post(config.endpoint)

    print("HTTP Status:", response.status_code)
    print("Response:", response.text)


if __name__ == "__main__":
    main()