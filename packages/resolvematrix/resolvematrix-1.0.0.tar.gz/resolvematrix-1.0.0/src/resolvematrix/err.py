__all__ = ("ResolutionError",)


class ResolutionError(Exception):
    """Custom base exception for errors in the resolution matrix operations."""

    def __init__(self, message: str, original_exception: Exception | None = None):
        self.original_exception = original_exception
        if original_exception:
            message = f"{message}: {str(original_exception)}"
        super().__init__(message)
