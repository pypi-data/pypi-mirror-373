from typing import Optional

class WaConfig:
    def __init__(self, data: dict, authentication_gateway):
        try: rl = int(data.get("rate_limit"))
        except: rl = 150

        self.target_type: str = "WA"
        self.url: str = data["endpoint"]
        self.data: dict = data["data"]
        self.concurrency: Optional[int] = None
        self.rate_limit: Optional[int] = rl
        self.response_size: Optional[int] = None
        self.bulk_size: Optional[int] = None
        self.timeout: Optional[int] = None

    def authenticate(self):
        self.credentials = self.authentication_gateway.get_credentials()
        if self.credentials is not None:
            self.data["headers"][self.credentials[0]] = self.credentials[1]