class AiriaAPIError(Exception):
    """
    Custom exception for Airia API errors.

    This exception is raised when an API request to the Airia service fails.
    It contains both the HTTP status code and error message to help with
    debugging and proper error handling.

    Attributes:
        status_code (int): The HTTP status code returned by the API
        message (str): The error message describing what went wrong
    """

    def __init__(self, status_code: int, message: str):
        """
        Initialize the exception with a status code and error message.

        Args:
            status_code (int): The HTTP status code of the failed request
            message (str): A descriptive error message
        """
        super().__init__(f"{status_code}: {message}")
        self.status_code = status_code
        self.message = message

    def __str__(self) -> str:
        """
        Return a string representation of the exception.

        Returns:
            str: A formatted string containing the status code and message
        """
        return f"{self.status_code}: {self.message}"
