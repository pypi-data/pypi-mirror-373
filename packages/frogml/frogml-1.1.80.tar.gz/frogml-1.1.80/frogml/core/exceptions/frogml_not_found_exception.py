from .frogml_exception import FrogmlException


class FrogmlNotFoundException(FrogmlException):
    def __init__(self, message):
        self.message = message
