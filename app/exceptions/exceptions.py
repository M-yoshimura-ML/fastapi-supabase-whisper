class UserAlreadyExistsException(Exception):
    def __init__(self, message="Email already registered"):
        self.message = message
        super().__init__(self.message)


class InvalidCredentialException(Exception):
    def __init__(self, message="Invalid credentials"):
        self.message = message
        super().__init__(self.message)


class NotFoundException(Exception):
    def __init__(self, message="Not Found", item: str = " "):
        self.message = item + message
        super().__init__(self.message)


class NoAccessConversationException(Exception):
    def __init__(self, message="Don't have access to this conversation or There is no conversation."):
        self.message = message
        super().__init__(self.message)

