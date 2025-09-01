from qwak.exceptions import QuietError


class QwakExternalException(QuietError):
    """
    An external system to Qwak, had an internal error
    """

    def __init__(self, message):
        super().__init__(message)
        self.message = message
