"""
    MoOGLi specific exception
"""


class MessageException(Exception):
    """
    Base class for passing messages in exceptions
    """

    def __init__(self, *args, **kwargs):
        super(Exception, self).__init__(*args, **kwargs)
        message = "Aucun message fournit"
        if "message" in kwargs:
            message = kwargs["message"]
        elif len(args) > 0:
            message = args[0]
        self.message: str = message


class BadRequest(Exception):
    """
    Exception raised when the request is invalid (form invalid datas ...)
    """

    message = "La requête est incorrecte"

    def __init__(self, message=None):
        if message:
            self.message = message

    def messages(self):
        """
        Used to fit colander's Invalid exception api
        """
        return [self.message]

    def asdict(self, translate=None):
        return {"erreur": self.message}


class Forbidden(Exception):
    """
    Forbidden exception, used to raise a forbidden action error
    """

    message = "Vous n'êtes pas autorisé à effectuer cette action"


class SignatureError(Forbidden):
    """
    Exception for status modification calls with the wrong signature
    """

    message = "Des informations manquent pour effectuer cette action"


class ExceptionWithKeyWords(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args)
        for key, value in list(kwargs.items()):
            setattr(self, key, value)


class MissingConfigError(ExceptionWithKeyWords):
    """
    Exception raised when a required configuration is missing

    .. code-block:: python

        raise MissingConfigError(
            message="Le nom n'est pas configuré",
            url="/admin/"
        )
    """
