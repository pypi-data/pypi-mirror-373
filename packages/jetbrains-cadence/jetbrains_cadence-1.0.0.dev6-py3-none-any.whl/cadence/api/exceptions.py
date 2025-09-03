class CadenceServerException(RuntimeError):
    def __init__(self, message: str, status: int):
        self.message = message
        self.status = status

    def __str__(self):
        return f"Got HTTP status {self.status} with message: {self.message}"
