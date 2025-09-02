class YourAPIError(Exception): ...


class APIConnectionError(YourAPIError): ...


class APITimeoutError(YourAPIError): ...


class APIResponseError(YourAPIError):
    def __init__(self, status: int, message: str):
        super().__init__(f"{status}: {message}")
        self.status, self.message = status, message
