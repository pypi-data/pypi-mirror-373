class FrogmlDecodeException(ValueError):
    """
    Failed to decode payload
    """

    def __init__(self, message):
        self.message = message
