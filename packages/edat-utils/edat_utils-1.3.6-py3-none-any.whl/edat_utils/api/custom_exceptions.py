
class ExpiredTokenException(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message
    
    def __repr__(self):
        return self.__str__()


class ApiGraphiqlExeception(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message
    
    def __repr__(self):
        return self.__str__()


class AccessDeniedException(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message
    
    def __repr__(self):
        return self.__str__()

