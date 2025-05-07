class UserAlreadyExistsException(Exception):
    def __init__(self, message="Email already registered"):
        self.message = message
        super().__init__(self.message)


class InvalidCredentialException(Exception):
    def __init__(self, message="Invalid credentials"):
        self.message = message
        super().__init__(self.message)

