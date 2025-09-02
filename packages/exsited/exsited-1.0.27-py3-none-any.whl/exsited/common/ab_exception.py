class ABException(Exception):
    raw_response: any = None
    errors: list = []

    def __init__(self, message=None, exception_type: str = None):
        super().__init__(message)
        self.exception_type = exception_type
        self.message = message

    def add_raw_response(self, raw_response: any):
        self.raw_response = raw_response
        return self

    def add_error(self, error: any):
        self.errors.append(error)

    def get_errors(self):
        return self.errors
