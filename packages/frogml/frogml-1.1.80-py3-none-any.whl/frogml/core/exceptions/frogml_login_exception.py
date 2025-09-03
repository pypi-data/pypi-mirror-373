from .quiet_error import QuietError


class FrogmlLoginException(QuietError):
    def __init__(
        self, message="Failed to login to Frogml. Please check your credentials"
    ):
        self.message = message
