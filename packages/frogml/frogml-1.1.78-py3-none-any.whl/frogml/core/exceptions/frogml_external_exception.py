from frogml.core.exceptions import QuietError


class FrogmlExternalException(QuietError):
    """
    An external system to Frogml, had an internal error
    """

    def __init__(self, message):
        super().__init__(message)
        self.message = message
