from typing import Optional


class V8ApiError(Exception):
    """Exception raised for V8 API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None, response_text: Optional[str] = None):
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(message) 