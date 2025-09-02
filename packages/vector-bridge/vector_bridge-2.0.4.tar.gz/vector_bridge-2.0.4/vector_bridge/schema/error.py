class HTTPException(Exception):
    """
    Custom exception for handling HTTP errors.

    Attributes:
        status_code (int): HTTP status code of the error.
        detail (str): Detailed error message.
    """

    def __init__(self, status_code: int, detail: str, *args, **kwargs):
        super().__init__(f"HTTP {status_code}: {detail}")
        self.status_code = status_code
        self.detail = detail
