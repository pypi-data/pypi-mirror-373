class ValidationError(Exception):
    def __init__(self, message: str):
        self.message = message


class BlastError(Exception):
    def __init__(self, message: str):
        self.message = message
