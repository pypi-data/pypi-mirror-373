########################################################################################################################
# CLASSES


class RedirectionDetectedError(Exception):
    def __init__(self, message="Redirection detected!"):
        self.message = message
        super().__init__(self.message)


class NotFoundError(Exception):
    def __init__(self, message="Not found!"):
        self.message = message
        super().__init__(self.message)
