class APIConfig:

    def __init__(self, base_url, api_key, api_secret):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.api_secret = api_secret

    @property
    def endpoint(self):
        return (
            self.base_url
            + "/api/licensed-consumer/getLatestSIFNavEntries"
        )