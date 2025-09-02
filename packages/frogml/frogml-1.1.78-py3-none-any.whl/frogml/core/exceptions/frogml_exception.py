from .quiet_error import QuietError


class FrogmlException(QuietError):
    def __init__(self, message, status_code=None):
        self.message = message
        self.status_code = status_code
