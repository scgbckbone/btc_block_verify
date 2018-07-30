
class MyBaseException(Exception):
    def __init__(self, msg):
        self.msg = msg


class NoDataProvidedError(MyBaseException):
    """
    Raised if no sufficient data were provided to initialize
    BTCBlock object.
    """


class IncorrectDataProvidedError(MyBaseException):
    """
    Raised if incorrect data were provided.
    """
